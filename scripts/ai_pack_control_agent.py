#!/usr/bin/env python3
"""Restricted host-side controller for the four allowlisted Yarsalam AI Packs."""
from __future__ import annotations

import json, os, re, secrets, subprocess, tempfile, threading, time, uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(os.getenv("AI_PACKS_ROOT", "/home/deploy/ai-packs-control-20261030"))
ENV_DIR = Path(os.getenv("AI_PACK_ENV_DIR", "/home/deploy/.config/yarsalam/ai-packs"))
SCRIPT_DIR = Path(os.getenv("AI_PACK_SCRIPT_DIR", "/home/deploy/.local/lib/yarsalam-ai-pack-control"))
REPORT_DIR = Path(os.getenv("AI_PACK_REPORT_DIR", "/home/deploy/ai-pack-deploy-logs/control"))
TOKEN = os.getenv("AI_PACK_CONTROL_TOKEN", "")
BIND = os.getenv("AI_PACK_CONTROL_BIND", "127.0.0.1")
PORT = int(os.getenv("AI_PACK_CONTROL_PORT", "9115"))
MIN_START_MB = int(os.getenv("AI_PACK_MIN_START_MB", "2500"))
MIN_RESERVE_MB = int(os.getenv("AI_PACK_MIN_RESERVE_MB", "1536"))
EMERGENCY_MB = int(os.getenv("AI_PACK_EMERGENCY_MB", "1024"))
COMPOSE_TIMEOUT = int(os.getenv("AI_PACK_COMPOSE_TIMEOUT", "1200"))
SMOKE_TIMEOUT = int(os.getenv("AI_PACK_SMOKE_TIMEOUT", "120"))

PACKS = {
    "matching-pack": ("yarsalam-matching-pack", "matching-pack.json", 9003, "MATCHING_PACK_ADMIN_TOKEN"),
    "seo-pack": ("yarsalam-seo-pack", "seo-pack.json", 9000, "SEO_PACK_ADMIN_TOKEN"),
    "revenue-pack": ("yarsalam-revenue-pack", "revenue-pack.json", 9002, "REVENUE_PACK_ADMIN_TOKEN"),
    "safety-pack": ("yarsalam-safety-pack", "safety-pack.yaml", 9001, "SAFETY_PACK_ADMIN_TOKEN"),
}
ORDER = tuple(PACKS)
JOBS: dict[str, dict[str, Any]] = {}
JOBS_LOCK = threading.Lock()
OP_LOCK = threading.Lock()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_env(path: Path) -> dict[str, str]:
    result = {}
    if not path.is_file():
        return result
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def mem() -> dict[str, int]:
    values = {}
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, rest = line.split(":", 1)
            values[key] = int(rest.strip().split()[0]) // 1024
    except Exception:
        pass
    return {"total_mb": values.get("MemTotal", 0), "available_mb": values.get("MemAvailable", 0),
            "swap_total_mb": values.get("SwapTotal", 0), "swap_free_mb": values.get("SwapFree", 0)}


def base(pack: str) -> list[str]:
    project, filename, _, _ = PACKS[pack]
    compose = ROOT / "deploy" / "compose" / filename
    env = ENV_DIR / f"{pack}.env"
    if not compose.is_file() or not env.is_file():
        raise RuntimeError(f"Compose or private env file missing for {pack}")
    return ["docker", "compose", "--parallel", "1", "--project-name", project,
            "--env-file", str(env), "-f", str(compose)]


def run(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=timeout, check=False)


def preflight(pack: str) -> dict[str, Any]:
    try:
        cmd = base(pack)
        services = run(cmd + ["config", "--services"], 30)
        images = run(cmd + ["config", "--images"], 30)
        if services.returncode or images.returncode:
            raise RuntimeError("Compose config validation failed")
        names = [x.strip() for x in services.stdout.splitlines() if x.strip()]
        all_images = [x.strip() for x in images.stdout.splitlines() if x.strip()]
        pack_images = [x for x in all_images if x.startswith("ghcr.io/yarsalam/ai-packs/")]
        unpinned = [x for x in pack_images if not re.search(r":sha-[0-9a-f]{40}$", x)]
        if unpinned:
            return {"ready": False, "reason": "non-immutable AI Pack image tag", "services": names}
        missing = [x for x in pack_images if run(["docker", "image", "inspect", x], 20).returncode]
        if missing:
            return {"ready": False, "reason": "immutable images missing locally; pull is disabled", "missing_images": missing, "services": names}
        token = read_env(ENV_DIR / f"{pack}.env").get(PACKS[pack][3], "")
        if len(token) < 32:
            return {"ready": False, "reason": "private gateway admin token missing/invalid", "services": names}
        return {"ready": True, "services": names, "images": pack_images}
    except Exception as exc:
        return {"ready": False, "reason": f"{type(exc).__name__}: {exc}"}


def containers(pack: str) -> list[dict[str, Any]]:
    project = PACKS[pack][0]
    result = run(["docker", "ps", "-a", "--filter", f"label=com.docker.compose.project={project}",
                  "--format", "{{json .}}"], 30)
    found = []
    if result.returncode:
        return found
    for line in result.stdout.splitlines():
        try:
            summary = json.loads(line)
            cid = summary.get("ID")
            raw = json.loads(run(["docker", "inspect", cid], 20).stdout)[0]
            state = raw.get("State", {})
            labels = raw.get("Config", {}).get("Labels") or {}
            found.append({
                "name": raw.get("Name", "").lstrip("/"),
                "service": labels.get("com.docker.compose.service", "unknown"),
                "state": state.get("Status", "unknown"),
                "health": (state.get("Health") or {}).get("Status", "no-healthcheck"),
                "exit_code": state.get("ExitCode"),
                "image": raw.get("Config", {}).get("Image", ""),
            })
        except Exception:
            continue
    return found


def gateway(pack: str) -> dict[str, Any]:
    url = f"http://127.0.0.1:{PACKS[pack][2]}/health"
    try:
        with urlopen(Request(url, headers={"Accept": "application/json"}), timeout=10) as r:
            body, code = r.read(512 * 1024), r.status
    except HTTPError as exc:
        body, code = exc.read(512 * 1024), exc.code
    except (URLError, TimeoutError, OSError) as exc:
        return {"http_status": None, "status": "unreachable", "error": f"{type(exc).__name__}: {exc}"}
    try:
        return {"http_status": code, **json.loads(body.decode("utf-8"))}
    except Exception:
        return {"http_status": code, "status": "invalid_response"}


def status(pack: str) -> dict[str, Any]:
    check = preflight(pack)
    c = containers(pack)
    running = sum(x["state"] == "running" for x in c)
    completed = sum(x["state"] == "exited" and x["exit_code"] == 0 for x in c)
    expected = len(check.get("services", []))
    state = ("stopped" if check.get("ready") else "not_installed") if not c else (
        "stopped" if not running else "running" if expected > 0 and running + completed >= expected else "partial"
    )
    project = PACKS[pack][0] + "-"
    stats = run(["docker", "stats", "--no-stream", "--format", "{{.Name}}|{{.MemUsage}}"], 30)
    mem_rows = []
    if stats.returncode == 0:
        for line in stats.stdout.splitlines():
            if line.startswith(project):
                name, _, usage = line.partition("|")
                mem_rows.append({"container": name, "usage": usage})
    return {"id": pack, "state": state, "running_containers": running, "containers": c,
            "gateway": gateway(pack) if running else {"status": "stopped"},
            "memory": mem_rows, "ready_to_start": bool(check.get("ready")),
            "preflight_reason": check.get("reason"), "missing_images": check.get("missing_images", [])}


def sample(job: dict[str, Any]) -> None:
    snap = mem()
    job["memory_samples"].append({"time": utcnow(), **snap})
    job["min_available_mb"] = min(job["min_available_mb"], snap["available_mb"] or job["min_available_mb"])
    job["current_memory"] = snap


def sampled_process(job: dict[str, Any], args: list[str], timeout: int) -> tuple[int, str]:
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        p = subprocess.Popen(args, stdout=out, stderr=err)
        began = time.monotonic()
        emergency = False
        while p.poll() is None:
            sample(job)
            if job["current_memory"]["available_mb"] < EMERGENCY_MB:
                emergency = True
                p.terminate()
                break
            if time.monotonic() - began > timeout:
                p.terminate()
                break
            time.sleep(1)
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()
        out.seek(0); err.seek(0)
        text = (out.read(500_000) + b"\n" + err.read(500_000)).decode("utf-8", errors="replace")
    return p.returncode or 0, text[-1800:] + ("; emergency memory guard" if emergency else "")


def start_pack(pack: str, job: dict[str, Any]) -> dict[str, Any]:
    check = preflight(pack)
    if not check.get("ready"):
        return {"ok": False, "reason": check.get("reason"), "preflight": check}
    before = mem()
    if before["available_mb"] < MIN_START_MB:
        return {"ok": False, "reason": "memory start guard", "before": before, "minimum_start_mb": MIN_START_MB}
    job["step"] = f"starting {pack}"
    code, detail = sampled_process(job, base(pack) + [
        "up", "-d", "--pull", "never", "--wait", "--wait-timeout", str(COMPOSE_TIMEOUT)
    ], COMPOSE_TIMEOUT + 60)
    after = mem()
    if code:
        run(base(pack) + ["stop"], 180)
        return {"ok": False, "reason": "Compose start/health failed", "detail": detail, "before": before, "after": after}
    if after["available_mb"] < MIN_RESERVE_MB or job["min_available_mb"] < MIN_RESERVE_MB:
        run(base(pack) + ["stop"], 180)
        return {"ok": False, "reason": "memory reserve breached; only newly-started pack stopped",
                "before": before, "after": after, "min_available_mb": job["min_available_mb"]}
    return {"ok": True, "before": before, "after": after, "services": check.get("services", [])}


def stop_pack(pack: str) -> dict[str, Any]:
    if not (ROOT / "deploy" / "compose" / PACKS[pack][1]).is_file() or not (ENV_DIR / f"{pack}.env").is_file():
        return {"ok": True, "skipped": True, "reason": "not installed"}
    result = run(base(pack) + ["stop"], 240)
    return {"ok": result.returncode == 0, "detail": result.stderr[-500:],
            "note": "Compose stop preserves images and named volumes"}


def test_pack(pack: str, job: dict[str, Any]) -> dict[str, Any]:
    env = read_env(ENV_DIR / f"{pack}.env")
    token_name = PACKS[pack][3]
    if len(env.get(token_name, "")) < 32:
        return {"ok": False, "reason": f"{token_name} missing"}
    try:
        import sys
        sys.path.insert(0, str(SCRIPT_DIR))
        import smoke_test_packs
        previous = os.environ.get(token_name)
        os.environ[token_name] = env[token_name]
        try:
            cfg = smoke_test_packs.PACKS[pack]
            result_box: dict[str, Any] = {}
            error_box: dict[str, str] = {}
            done = threading.Event()
            def call() -> None:
                try:
                    result_box["value"] = smoke_test_packs.test_pack(
                        pack, cfg, Path("/nonexistent"), None, SMOKE_TIMEOUT
                    )
                except Exception as exc:
                    error_box["message"] = f"{type(exc).__name__}: {exc}"
                finally:
                    done.set()
            thread = threading.Thread(target=call, daemon=True); thread.start()
            while not done.wait(1): sample(job)
            thread.join()
            if error_box: raise RuntimeError(error_box["message"])
            result = result_box["value"]
        finally:
            if previous is None: os.environ.pop(token_name, None)
            else: os.environ[token_name] = previous
    except Exception as exc:
        return {"ok": False, "reason": f"smoke test error: {type(exc).__name__}: {exc}"}
    health = gateway(pack)
    tests = result.get("tests", [])
    failed = [x for x in tests if x.get("status") != "PASS"]
    egress = None
    if pack == "seo-pack":
        url_test = next((x for x in tests if "URL technical HTML audit" in x.get("test", "")), None)
        egress = "external_url_fetch_passed" if url_test and url_test.get("status") == "PASS" else "VPN_OR_OUTBOUND_EGRESS_BLOCKED_OR_REQUIRED"
    model_readiness = None
    if pack == "revenue-pack":
        model_readiness = {
            name: {k: v for k, v in data.items() if k in {"model_trained", "cv_score", "model_phase", "training_samples"}}
            for name, data in (health.get("services") or {}).items() if isinstance(data, dict)
        }
    return {"ok": not failed and health.get("status") == "healthy", "health": health,
            "tests": tests, "failed_tests": len(failed), "seo_external_egress": egress,
            "revenue_model_readiness": model_readiness,
            "warning": "Smoke tests do not prove model quality, calibration, legal clearance, or commercial readiness."}


def progressive(job: dict[str, Any]) -> dict[str, Any]:
    results = []
    for pack in ORDER:
        job["step"] = f"checking {pack}"
        before_status = status(pack)
        if before_status["state"] == "not_installed":
            results.append({"pack": pack, "state": "skipped_not_installed",
                            "reason": before_status.get("preflight_reason")})
            continue
        already = before_status["state"] == "running"
        if not already:
            started = start_pack(pack, job)
            if not started.get("ok"):
                results.append({"pack": pack, "state": "not_started", "start": started, "memory": mem()})
                if started.get("reason") in {"memory start guard", "memory reserve breached; only newly-started pack stopped"}:
                    break
                continue
        else:
            started = {"ok": True, "already_running": True}
        job["step"] = f"functional test {pack}"
        tested = test_pack(pack, job)
        after = mem()
        reserve = after["available_mb"] < MIN_RESERVE_MB or job["min_available_mb"] < MIN_RESERVE_MB
        gateway_unavailable = tested.get("health", {}).get("status") in {"unreachable", "unavailable"}
        stopped = None
        if not already and (reserve or gateway_unavailable):
            job["step"] = f"stopping newly-started {pack}"
            stopped = stop_pack(pack)
        results.append({
            "pack": pack, "state": "tested", "was_running_before": already, "start": started,
            "test": tested, "memory_after": after, "minimum_available_during_operation_mb": job["min_available_mb"],
            "reserve_breached": reserve, "stopped_by_guard": stopped,
            "memory_samples": job["memory_samples"][-120:],
        })
        if reserve:
            break
    return {"packs": results, "memory_after": mem(),
            "thresholds": {"minimum_start_mb": MIN_START_MB, "minimum_reserve_mb": MIN_RESERVE_MB,
                           "emergency_mb": EMERGENCY_MB},
            "policy": "Only a newly-started pack may be auto-stopped by health/memory guards; pre-existing packs are preserved."}


def execute(kind: str, pack: str | None, actor: str) -> tuple[int, dict[str, Any]]:
    if not OP_LOCK.acquire(blocking=False):
        return 409, {"error": "another AI Pack operation is running"}
    job_id = uuid.uuid4().hex[:16]
    job = {"id": job_id, "kind": kind, "actor": actor, "state": "queued", "step": "queued",
           "created_at": utcnow(), "updated_at": utcnow(), "memory_samples": [],
           "min_available_mb": mem()["available_mb"], "result": None, "error": None}
    with JOBS_LOCK: JOBS[job_id] = job
    def worker() -> None:
        job["state"] = "running"
        try:
            if kind == "progressive":
                result = progressive(job)
            elif kind == "stop-all":
                result = {name: stop_pack(name) for name in reversed(ORDER)}
            elif kind == "start":
                result = start_pack(pack, job)  # type: ignore[arg-type]
            elif kind == "stop":
                result = stop_pack(pack)  # type: ignore[arg-type]
            elif kind == "test":
                if status(pack)["state"] != "running":  # type: ignore[arg-type]
                    result = {"ok": False, "reason": "pack is not running"}
                else:
                    result = test_pack(pack, job)  # type: ignore[arg-type]
            else:
                result = {"error": "unsupported operation"}
            job.update(state="completed", step="completed", result=result)
            REPORT_DIR.mkdir(parents=True, exist_ok=True)
            (REPORT_DIR / f"{job_id}.json").write_text(json.dumps(job, ensure_ascii=False, indent=2) + "\n")
        except Exception as exc:
            job.update(state="failed", step="failed", error=f"{type(exc).__name__}: {exc}")
        finally:
            job["updated_at"] = utcnow()
            OP_LOCK.release()
    threading.Thread(target=worker, daemon=True).start()
    return 202, {"job_id": job_id, "state": "queued", "kind": kind}


class Handler(BaseHTTPRequestHandler):
    server_version = "YarsalamPackControl/1.0"
    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"{utcnow()} {self.client_address[0]} {fmt % args}", flush=True)
    def send_json(self, code: int, value: dict[str, Any]) -> None:
        data = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data))); self.send_header("Cache-Control", "no-store")
        self.end_headers(); self.wfile.write(data)
    def authorized(self) -> bool:
        header = self.headers.get("Authorization", "")
        return bool(TOKEN) and header.startswith("Bearer ") and secrets.compare_digest(header[7:], TOKEN)
    def body(self) -> dict[str, Any]:
        size = int(self.headers.get("Content-Length", "0"))
        if size < 0 or size > 4096: raise ValueError("bad body size")
        value = json.loads(self.rfile.read(size) if size else b"{}")
        if not isinstance(value, dict): raise ValueError("JSON object required")
        return value
    def do_GET(self) -> None:
        if not self.authorized(): self.send_json(401, {"error": "unauthorized"}); return
        if self.path == "/v1/status":
            self.send_json(200, {"timestamp": utcnow(), "memory": mem(),
                "packs": {name: status(name) for name in PACKS}, "operation_running": OP_LOCK.locked()}); return
        match = re.fullmatch(r"/v1/jobs/([a-f0-9]{16})", self.path)
        if match:
            with JOBS_LOCK: job = JOBS.get(match.group(1))
            self.send_json(200, dict(job) if job else {"error": "job_not_found"}); return
        self.send_json(404, {"error": "not_found"})
    def do_POST(self) -> None:
        if not self.authorized(): self.send_json(401, {"error": "unauthorized"}); return
        try: body = self.body()
        except Exception: self.send_json(400, {"error": "invalid_json"}); return
        actor = re.sub(r"[^A-Za-z0-9_.@:-]", "", self.headers.get("X-Admin-Actor", "admin"))[:80] or "admin"
        if self.path == "/v1/test-progressive":
            code, out = execute("progressive", None, actor)
        elif self.path == "/v1/stop-all":
            if body.get("confirm") is not True: self.send_json(400, {"error": "explicit confirmation required"}); return
            code, out = execute("stop-all", None, actor)
        else:
            match = re.fullmatch(r"/v1/packs/(matching-pack|seo-pack|revenue-pack|safety-pack)/(start|stop|test)", self.path)
            if not match: self.send_json(404, {"error": "not_found"}); return
            pack, action = match.groups()
            code, out = execute(action, pack, actor)
        self.send_json(code, out)


def main() -> int:
    if len(TOKEN) < 48: raise SystemExit("AI_PACK_CONTROL_TOKEN must be a random secret of at least 48 characters")
    gateway = run(["docker", "network", "inspect", "yarsalam_network",
                   "--format", "{{(index .IPAM.Config 0).Gateway}}"], 20)
    if gateway.returncode != 0 or gateway.stdout.strip() != BIND:
        raise SystemExit("AI_PACK_CONTROL_BIND must exactly match the yarsalam_network gateway IP")
    if BIND in {"0.0.0.0", "::", "127.0.0.1"}:
        raise SystemExit("Bind only to the private yarsalam_network gateway IP")
    httpd = ThreadingHTTPServer((BIND, PORT), Handler)
    print(f"Yarsalam AI Pack controller listening on private bridge {BIND}:{PORT}", flush=True)
    httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
