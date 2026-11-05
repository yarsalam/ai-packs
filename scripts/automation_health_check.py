#!/usr/bin/env python3
"""Read-only, sanitized GitHub Actions health snapshot. No logs or artifacts are read."""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

def iso(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except (AttributeError, TypeError, ValueError):
        return None

def get_json(api_url, token, path):
    req = Request(api_url.rstrip("/") + path, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + token,
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ai-packs-automation-health",
    })
    try:
        with urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, ValueError, UnicodeDecodeError):
        raise RuntimeError("GitHub API request failed; diagnostic details redacted")
    if not isinstance(data, dict):
        raise RuntimeError("Unexpected GitHub API response shape; details redacted")
    return data

def snapshot(repo, reader, now=None, current_run_id=None):
    now = now or datetime.now(timezone.utc)
    workflows = reader(f"/repos/{repo}/actions/workflows?per_page=100").get("workflows", [])
    runs = reader(f"/repos/{repo}/actions/runs?branch=main&per_page=50").get("workflow_runs", [])
    health = next((w for w in workflows if w.get("path") == ".github/workflows/automation-health.yml"), None)
    schedule_state, previous = "workflow_not_found", None
    if health and health.get("id") is not None:
        scheduled = reader(f"/repos/{repo}/actions/workflows/{health['id']}/runs?per_page=20").get("workflow_runs", [])
        scheduled = [r for r in scheduled if r.get("event") == "schedule" and str(r.get("id")) != str(current_run_id or "")]
        scheduled.sort(key=lambda r: iso(r.get("created_at")) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        previous = scheduled[0] if scheduled else None
        if previous is None:
            schedule_state = "baseline_pending"
        else:
            dt = iso(previous.get("created_at"))
            schedule_state = "stale" if dt is None or now - dt > timedelta(hours=36) else "fresh"

    failures = []
    for r in runs:
        created = iso(r.get("created_at"))
        if r.get("status") == "completed" and r.get("conclusion") == "failure" and created and now - created <= timedelta(hours=24):
            failures.append({"workflow": r.get("name", "unnamed"), "sha": (r.get("head_sha") or "")[:7], "url": r.get("html_url", "")})

    stale = []
    active = [r for r in runs if r.get("status") in ("queued", "in_progress")][:10]
    for r in active:
        run_id = r.get("id")
        if run_id is None:
            continue
        jobs = reader(f"/repos/{repo}/actions/runs/{run_id}/jobs?per_page=100").get("jobs", [])
        for job in jobs:
            status = job.get("status")
            stamp = job.get("created_at") if status == "queued" else job.get("started_at")
            if status == "queued":
                threshold = timedelta(minutes=30)
            elif status == "in_progress":
                threshold = timedelta(minutes=300)
                stamp = stamp or r.get("created_at")
            else:
                continue
            dt = iso(stamp)
            if dt and now - dt > threshold:
                stale.append({"workflow": r.get("name", "unnamed"), "job": job.get("name", "unnamed"), "status": status, "minutes": int((now-dt).total_seconds() // 60), "sha": (r.get("head_sha") or "")[:7], "url": r.get("html_url", "")})

    issues = []
    if failures:
        issues.append("recent_main_workflow_failures")
    if stale:
        issues.append("stale_jobs_detected")
    if schedule_state == "stale":
        issues.append("scheduled_health_run_stale")
    if schedule_state == "workflow_not_found":
        issues.append("health_workflow_not_visible")
    status = "degraded" if issues else ("baseline_pending" if schedule_state == "baseline_pending" else "healthy")
    return {"status": status, "checked_at": now.isoformat(timespec="seconds"), "workflows": len(workflows),
            "inactive_workflows": [w.get("name", "unnamed") for w in workflows if w.get("state") != "active"],
            "main_runs_checked": len(runs), "schedule_state": schedule_state,
            "previous_schedule": ({"created_at": previous.get("created_at"), "conclusion": previous.get("conclusion")} if previous else None),
            "recent_failures": failures[:10], "stale_jobs": stale[:20], "issues": issues}

def render(report):
    lines = ["## AI Packs GitHub automation health", "", f"- **Status:** `{report['status']}`",
             f"- **Checked (UTC):** `{report['checked_at']}`", f"- **Workflows:** {report['workflows']}",
             f"- **Main runs inspected:** {report['main_runs_checked']}", f"- **Scheduled health:** `{report['schedule_state']}`"]
    if report["previous_schedule"]:
        p = report["previous_schedule"]
        lines.append(f"- **Previous scheduled run:** `{p['created_at']}` (`{p.get('conclusion') or 'unknown'}`)")
    if report["inactive_workflows"]:
        lines.append("- **Inactive workflows:** " + ", ".join(report["inactive_workflows"][:10]))
    if report["recent_failures"]:
        lines += ["", "### Recent main failures"]
        lines += [f"- [{x['workflow']}]({x['url']}) — `{x['sha']}`" for x in report["recent_failures"]]
    if report["stale_jobs"]:
        lines += ["", "### Stale jobs"]
        lines += [f"- [{x['workflow']}]({x['url']}) / {x['job']} — {x['status']}, {x['minutes']} min, `{x['sha']}`" for x in report["stale_jobs"]]
    if report["issues"]:
        lines += ["", "### Conditions"] + [f"- `{x}`" for x in report["issues"]]
    elif report["status"] == "baseline_pending":
        lines += ["", "First scheduled execution is still needed to establish a baseline."]
    else:
        lines += ["", "No stale jobs or recent main-branch failures were detected."]
    lines += ["", "_Read-only metadata only: no logs/artifacts, issue writes, secrets, cancellation, retry, merge, publish or deploy._"]
    return "\n".join(lines) + "\n"

def main():
    repo, token = os.getenv("GITHUB_REPOSITORY", ""), os.getenv("GITHUB_TOKEN", "")
    if not repo or not token:
        print("Health monitor configuration missing; details redacted.", file=sys.stderr)
        return 2
    api = os.getenv("GITHUB_API_URL", "https://api.github.com")
    try:
        report = snapshot(repo, lambda p: get_json(api, token, p), current_run_id=os.getenv("GITHUB_RUN_ID"))
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    summary = render(report)
    path = os.getenv("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as out:
            out.write(summary)
    print("AI Packs health status: " + report["status"] + "; see sanitized job summary.")
    return 1 if report["status"] == "degraded" else 0

if __name__ == "__main__":
    raise SystemExit(main())
