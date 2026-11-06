#!/usr/bin/env python3
"""Read-only, sanitized GitHub Actions health snapshot. No logs or artifacts are read."""
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MAX_API_ATTEMPTS = 3
TRANSIENT_HTTP_STATUSES = {408, 429, 502, 503, 504}
SCHEDULE_STALE_AFTER = timedelta(hours=36)
SUCCESS_STALE_AFTER = timedelta(hours=36)
MAX_ACTIVE_RUNS_TO_INSPECT = 10


def iso(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except (AttributeError, TypeError, ValueError):
        return None


def get_json(api_url, token, path, opener=None, sleeper=None):
    """GET JSON with at most three attempts for transient, idempotent failures."""
    opener = opener or urlopen
    sleeper = sleeper or time.sleep
    req = Request(api_url.rstrip("/") + path, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + token,
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ai-packs-automation-health",
    })

    for attempt in range(MAX_API_ATTEMPTS):
        try:
            with opener(req, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
            if not isinstance(data, dict):
                raise RuntimeError("Unexpected GitHub API response shape; details redacted")
            return data
        except HTTPError as exc:
            # The error is file-like; close its response body because it is never read.
            try:
                exc.close()
            except OSError:
                pass
            retryable = exc.code in TRANSIENT_HTTP_STATUSES
            if not retryable or attempt == MAX_API_ATTEMPTS - 1:
                raise RuntimeError("GitHub API request failed; diagnostic details redacted")
        except (URLError, TimeoutError, ConnectionError):
            if attempt == MAX_API_ATTEMPTS - 1:
                raise RuntimeError("GitHub API request failed; diagnostic details redacted")
        except (ValueError, UnicodeDecodeError):
            raise RuntimeError("GitHub API response was invalid; diagnostic details redacted")
        sleeper(min(2 ** attempt, 2))

    raise RuntimeError("GitHub API request failed; retry limit reached; details redacted")


def snapshot(repo, reader, now=None, current_run_id=None):
    now = now or datetime.now(timezone.utc)
    current_id = str(current_run_id or "")
    workflows = reader(f"/repos/{repo}/actions/workflows?per_page=100").get("workflows", [])
    runs = reader(f"/repos/{repo}/actions/runs?branch=main&per_page=50").get("workflow_runs", [])
    health = next((w for w in workflows if w.get("path") == ".github/workflows/automation-health.yml"), None)

    schedule_state, previous = "workflow_not_found", None
    if health and health.get("id") is not None:
        scheduled = reader(f"/repos/{repo}/actions/workflows/{health['id']}/runs?per_page=20").get("workflow_runs", [])
        scheduled = [
            r for r in scheduled
            if r.get("event") == "schedule" and str(r.get("id")) != current_id
        ]
        scheduled.sort(
            key=lambda r: iso(r.get("created_at")) or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        previous = scheduled[0] if scheduled else None
        if previous is None:
            schedule_state = "baseline_pending"
        else:
            scheduled_at = iso(previous.get("created_at"))
            if scheduled_at is None or now - scheduled_at > SCHEDULE_STALE_AFTER:
                schedule_state = "stale"
            elif previous.get("status") != "completed":
                schedule_state = "in_progress"
            elif previous.get("conclusion") != "success":
                schedule_state = "failed"
            else:
                schedule_state = "fresh"

    eligible_runs = [r for r in runs if str(r.get("id")) != current_id]
    successful = [
        r for r in eligible_runs
        if r.get("status") == "completed" and r.get("conclusion") == "success"
    ]
    successful.sort(
        key=lambda r: iso(r.get("created_at")) or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    last_success = successful[0] if successful else None
    last_success_state = "missing"
    if last_success:
        success_at = iso(last_success.get("created_at"))
        last_success_state = (
            "stale" if success_at is None or now - success_at > SUCCESS_STALE_AFTER else "fresh"
        )

    failures = []
    for run in eligible_runs:
        created = iso(run.get("created_at"))
        if (
            run.get("status") == "completed"
            and run.get("conclusion") == "failure"
            and created
            and timedelta(0) <= now - created <= timedelta(hours=24)
        ):
            failures.append({
                "workflow": run.get("name", "unnamed"),
                "sha": (run.get("head_sha") or "")[:7],
                "url": run.get("html_url", ""),
            })

    active = [
        r for r in eligible_runs
        if r.get("status") in ("queued", "in_progress")
    ]
    active.sort(
        key=lambda r: iso(r.get("created_at")) or datetime.max.replace(tzinfo=timezone.utc)
    )
    active_runs_truncated = len(active) > MAX_ACTIVE_RUNS_TO_INSPECT
    active = active[:MAX_ACTIVE_RUNS_TO_INSPECT]

    stale = []
    for run in active:
        run_id = run.get("id")
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
                stamp = stamp or run.get("created_at")
            else:
                continue
            started = iso(stamp)
            if started and now - started > threshold:
                stale.append({
                    "workflow": run.get("name", "unnamed"),
                    "job": job.get("name", "unnamed"),
                    "status": status,
                    "minutes": int((now - started).total_seconds() // 60),
                    "sha": (run.get("head_sha") or "")[:7],
                    "url": run.get("html_url", ""),
                })

    inactive = [w.get("name", "unnamed") for w in workflows if w.get("state") != "active"]
    issues = []
    if failures:
        issues.append("recent_main_workflow_failures")
    if stale:
        issues.append("stale_jobs_detected")
    if active_runs_truncated:
        issues.append("active_run_scan_truncated")
    if inactive:
        issues.append("inactive_workflows_detected")
    if last_success_state == "missing":
        issues.append("no_successful_main_run_found")
    elif last_success_state == "stale":
        issues.append("last_successful_main_run_stale")
    if schedule_state == "stale":
        issues.append("scheduled_health_run_stale")
    elif schedule_state == "failed":
        issues.append("last_scheduled_health_run_not_successful")
    elif schedule_state == "in_progress":
        issues.append("previous_scheduled_health_run_incomplete")
    elif schedule_state == "workflow_not_found":
        issues.append("health_workflow_not_visible")

    status = "degraded" if issues else (
        "baseline_pending" if schedule_state == "baseline_pending" else "healthy"
    )
    return {
        "status": status,
        "checked_at": now.isoformat(timespec="seconds"),
        "workflows": len(workflows),
        "inactive_workflows": inactive,
        "main_runs_checked": len(eligible_runs),
        "active_runs_checked": len(active),
        "active_runs_truncated": active_runs_truncated,
        "last_successful_main_run": ({
            "workflow": last_success.get("name", "unnamed"),
            "created_at": last_success.get("created_at"),
            "conclusion": last_success.get("conclusion"),
            "sha": (last_success.get("head_sha") or "")[:7],
            "url": last_success.get("html_url", ""),
        } if last_success else None),
        "last_success_state": last_success_state,
        "schedule_state": schedule_state,
        "previous_schedule": ({
            "created_at": previous.get("created_at"),
            "status": previous.get("status"),
            "conclusion": previous.get("conclusion"),
        } if previous else None),
        "recent_failures": failures[:10],
        "stale_jobs": stale[:20],
        "issues": issues,
    }


def render(report):
    lines = [
        "## AI Packs GitHub automation health",
        "",
        f"- **Status:** `{report['status']}`",
        f"- **Checked (UTC):** `{report['checked_at']}`",
        f"- **Workflows:** {report['workflows']}",
        f"- **Main runs inspected:** {report['main_runs_checked']}",
        f"- **Last successful main run:** `{report['last_success_state']}`",
        f"- **Scheduled health:** `{report['schedule_state']}`",
    ]
    if report["last_successful_main_run"]:
        item = report["last_successful_main_run"]
        lines.append(
            f"- **Last success:** [{item['workflow']}]({item['url']}) — "
            f"`{item['created_at']}`, SHA `{item['sha']}`"
        )
    if report["previous_schedule"]:
        item = report["previous_schedule"]
        lines.append(
            f"- **Previous scheduled run:** `{item['created_at']}` "
            f"(`{item.get('status') or 'unknown'} / {item.get('conclusion') or 'unknown'}`)"
        )
    if report["inactive_workflows"]:
        lines.append("- **Inactive workflows:** " + ", ".join(report["inactive_workflows"][:10]))
    if report["active_runs_truncated"]:
        lines.append("- **Active-run scan:** truncated at the oldest 10 active runs.")
    if report["recent_failures"]:
        lines += ["", "### Recent main failures"]
        lines += [f"- [{item['workflow']}]({item['url']}) — `{item['sha']}`" for item in report["recent_failures"]]
    if report["stale_jobs"]:
        lines += ["", "### Stale jobs"]
        lines += [
            f"- [{item['workflow']}]({item['url']}) / {item['job']} — "
            f"{item['status']}, {item['minutes']} min, `{item['sha']}`"
            for item in report["stale_jobs"]
        ]
    if report["issues"]:
        lines += ["", "### Conditions"] + [f"- `{item}`" for item in report["issues"]]
    elif report["status"] == "baseline_pending":
        lines += ["", "First successful scheduled execution is still needed to establish a baseline."]
    else:
        lines += ["", "No stale jobs or recent main-branch failures were detected."]
    lines += [
        "",
        "_Read-only metadata only: no logs/artifacts, issue writes, secrets, cancellation, "
        "merge, publish or deploy. API retries are limited to three attempts for transient GET failures._",
    ]
    return "\n".join(lines) + "\n"


def main():
    repo, token = os.getenv("GITHUB_REPOSITORY", ""), os.getenv("GITHUB_TOKEN", "")
    if not repo or not token:
        print("Health monitor configuration missing; details redacted.", file=sys.stderr)
        return 2
    api = os.getenv("GITHUB_API_URL", "https://api.github.com")
    try:
        report = snapshot(
            repo,
            lambda path: get_json(api, token, path),
            current_run_id=os.getenv("GITHUB_RUN_ID"),
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    summary = render(report)
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as output:
            output.write(summary)
    print("AI Packs health status: " + report["status"] + "; see sanitized job summary.")
    return 1 if report["status"] == "degraded" else 0


if __name__ == "__main__":
    raise SystemExit(main())
