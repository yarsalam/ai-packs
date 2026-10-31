#!/usr/bin/env bash
set -Eeuo pipefail

# Install the fixed-allowlist host controller and immediately run one progressive
# no-pull smoke/RAM assessment. No image build/pull or volume deletion is possible.

CONTROL_REF="${AI_PACK_CONTROL_REF:-feat/admin-ai-pack-control-and-progressive-test}"
RAW_BASE="https://raw.githubusercontent.com/yarsalam/ai-packs/${CONTROL_REF}"
HOME_DIR="${HOME:-/home/deploy}"
ROOT="$HOME_DIR/ai-packs-control-20261030"
ADMIN_ENV="$HOME_DIR/yarsalam-admin-prod-20261026/.env"
ENV_DIR="$HOME_DIR/.config/yarsalam/ai-packs"
AGENT_DIR="$HOME_DIR/.local/lib/yarsalam-ai-pack-control"
CONTROL_ENV="$ENV_DIR/control-agent.env"
REPORT_DIR="$HOME_DIR/ai-pack-deploy-logs/control"
UNIT_FILE="/etc/systemd/system/yarsalam-ai-pack-control.service"
PORT=9115

log() { printf '%s\n' "$*"; }
die() { log "ERROR: $*" >&2; exit 1; }

[[ "$(id -un)" == "deploy" ]] || die "Run as deploy user."
command -v docker >/dev/null 2>&1 || die "docker CLI not found."
command -v curl >/dev/null 2>&1 || die "curl not found."
command -v python3 >/dev/null 2>&1 || die "python3 not found."
command -v sudo >/dev/null 2>&1 || die "sudo not found."
docker info >/dev/null 2>&1 || die "deploy user cannot access Docker."
[[ -f "$ADMIN_ENV" ]] || die "Private admin env file missing: $ADMIN_ENV"
[[ -d "$ROOT/deploy/compose" ]] || die "AI Pack Compose directory missing."
[[ -d "$ENV_DIR" ]] || die "Private AI Pack env directory missing."

GATEWAY="$(docker network inspect yarsalam_network --format '{{(index .IPAM.Config 0).Gateway}}' 2>/dev/null || true)"
[[ "$GATEWAY" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]] || die "Cannot resolve yarsalam_network gateway."

TOKEN="$(python3 - "$ADMIN_ENV" <<'PY'
import sys
from pathlib import Path
for line in Path(sys.argv[1]).read_text(errors="replace").splitlines():
    if line.startswith("AI_PACK_CONTROL_TOKEN="):
        print(line.split("=", 1)[1].strip().strip('"').strip("'"))
        break
PY
)"
if [[ ${#TOKEN} -lt 48 ]]; then
  TOKEN="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
fi

mkdir -p "$AGENT_DIR" "$REPORT_DIR" "$ENV_DIR"
chmod 700 "$AGENT_DIR" "$REPORT_DIR" "$ENV_DIR"

# Only minimal runtime control code and the existing gateway smoke test are installed.
curl -fsSL --retry 3 "$RAW_BASE/scripts/ai_pack_control_agent.py" -o "$AGENT_DIR/ai_pack_control_agent.py"
curl -fsSL --retry 3 "$RAW_BASE/scripts/smoke_test_packs.py" -o "$AGENT_DIR/smoke_test_packs.py"
chmod 500 "$AGENT_DIR/ai_pack_control_agent.py" "$AGENT_DIR/smoke_test_packs.py"
python3 -m py_compile "$AGENT_DIR/ai_pack_control_agent.py" "$AGENT_DIR/smoke_test_packs.py"

# Preserve private .env files and write only the two control settings atomically.
python3 - "$ADMIN_ENV" "$CONTROL_ENV" "$GATEWAY" "$PORT" "$TOKEN" "$ROOT" "$ENV_DIR" "$AGENT_DIR" "$REPORT_DIR" <<'PY'
import os, shutil, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
admin, control, gateway, port, token, root, env_dir, agent_dir, report_dir = sys.argv[1:]
def update(path: Path, values: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    old = path.read_text(encoding="utf-8", errors="replace").splitlines() if path.exists() else []
    if path.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        shutil.copy2(path, path.with_name(path.name + "." + stamp + ".bak.ai-pack-control"))
    pending = dict(values)
    out = []
    for line in old:
        key = line.split("=", 1)[0].strip() if "=" in line and not line.lstrip().startswith("#") else None
        if key in pending:
            out.append(f"{key}={pending.pop(key)}")
        else:
            out.append(line)
    out.extend(f"{key}={value}" for key, value in pending.items())
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("\n".join(out).rstrip() + "\n")
            f.flush(); os.fsync(f.fileno())
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    finally:
        try: os.unlink(tmp)
        except FileNotFoundError: pass
update(Path(admin), {"AI_PACK_CONTROL_URL": f"http://{gateway}:{port}", "AI_PACK_CONTROL_TOKEN": token})
update(Path(control), {
    "AI_PACK_CONTROL_BIND": gateway,
    "AI_PACK_CONTROL_PORT": port,
    "AI_PACK_CONTROL_TOKEN": token,
    "AI_PACKS_ROOT": root,
    "AI_PACK_ENV_DIR": env_dir,
    "AI_PACK_SCRIPT_DIR": agent_dir,
    "AI_PACK_REPORT_DIR": report_dir,
    "AI_PACK_MIN_START_MB": "2500",
    "AI_PACK_MIN_RESERVE_MB": "1536",
    "AI_PACK_EMERGENCY_MB": "1024",
    "AI_PACK_COMPOSE_TIMEOUT": "1200",
    "AI_PACK_SMOKE_TIMEOUT": "120",
})
os.chmod(admin, 0o600)
os.chmod(control, 0o600)
PY

UNIT_TMP="$(mktemp)"
cat > "$UNIT_TMP" <<EOF
[Unit]
Description=Yarsalam restricted AI Pack control agent
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=simple
User=deploy
Group=deploy
SupplementaryGroups=docker
EnvironmentFile=$CONTROL_ENV
WorkingDirectory=$ROOT
ExecStart=/usr/bin/python3 $AGENT_DIR/ai_pack_control_agent.py
Restart=on-failure
RestartSec=3
UMask=0077
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=read-only
ReadWritePaths=$REPORT_DIR

[Install]
WantedBy=multi-user.target
EOF
sudo install -o root -g root -m 0644 "$UNIT_TMP" "$UNIT_FILE"
rm -f "$UNIT_TMP"
sudo systemctl daemon-reload
sudo systemctl enable --now yarsalam-ai-pack-control.service
sudo systemctl restart yarsalam-ai-pack-control.service

CONTROL_URL="http://$GATEWAY:$PORT"
READY=0
for _ in $(seq 1 20); do
  if curl -fsS --max-time 15 -H "Authorization: Bearer $TOKEN" "$CONTROL_URL/v1/status" >/dev/null 2>&1; then
    READY=1; break
  fi
  sleep 1
done
if [[ "$READY" != "1" ]]; then
  sudo systemctl --no-pager --full status yarsalam-ai-pack-control.service || true
  die "Control agent did not become ready; no Pack start operation was issued."
fi

RESPONSE="$(curl -fsS --max-time 10 -X POST -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{}' "$CONTROL_URL/v1/test-progressive")"
JOB_ID="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("job_id", ""))' <<<"$RESPONSE")"
[[ "$JOB_ID" =~ ^[a-f0-9]{16}$ ]] || die "Progressive test job was not accepted."

log "AI_PACK_CONTROL_AGENT=ACTIVE"
log "CONTROL_ENDPOINT=$CONTROL_URL (private Docker bridge only)"
log "PROGRESSIVE_TEST_JOB=$JOB_ID"
log "Sequence: existing Matching, then SEO, Revenue and Safety only if installed and memory guards allow."
log "SEO external URL audit will test VPN/outbound egress from inside the Pack."
while true; do
  JOB="$(curl -fsS --max-time 10 -H "Authorization: Bearer $TOKEN" "$CONTROL_URL/v1/jobs/$JOB_ID")"
  STATE="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("state", "unknown"))' <<<"$JOB")"
  STEP="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("step", ""))' <<<"$JOB")"
  printf 'JOB_STATE=%s | STEP=%s\n' "$STATE" "$STEP"
  case "$STATE" in completed|failed) break ;; esac
  sleep 5
done

log "===== PROGRESSIVE TEST RESULT ====="
python3 -m json.tool <<<"$JOB"
log "===== FINAL HOST RESOURCES ====="
free -h
docker stats --no-stream --format '{{.Name}} | CPU={{.CPUPerc}} | MEM={{.MemUsage}}' || true
log "REPORT_DIRECTORY=$REPORT_DIR"
log "NO_IMAGE_PULL_OR_BUILD=ENFORCED"
log "NO_VOLUMES_REMOVED=ENFORCED"
log "OTHER_PROJECTS_NOT_TARGETED=ENFORCED"
