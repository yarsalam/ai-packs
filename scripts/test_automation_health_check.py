import unittest
from datetime import datetime, timezone
from urllib.error import HTTPError

from scripts.automation_health_check import get_json, snapshot, render

NOW = datetime(2026, 11, 5, 12, 0, tzinfo=timezone.utc)
REPO = "yarsalam/ai-packs"
SUCCESS_RUN = {
    "id": 5,
    "name": "Gateway contract tests",
    "status": "completed",
    "conclusion": "success",
    "created_at": "2026-11-05T11:00:00Z",
    "head_sha": "1234567890",
    "html_url": "https://github.com/yarsalam/ai-packs/actions/runs/5",
}


def reader_for(main_runs=None, schedule_runs=None, jobs=None, workflow_state="active"):
    if main_runs is None:
        main_runs = [SUCCESS_RUN]
    if schedule_runs is None:
        schedule_runs = []
    if jobs is None:
        jobs = {}

    def read(path):
        if path.endswith("/actions/workflows?per_page=100"):
            return {"workflows": [{
                "id": 7,
                "name": "Health",
                "path": ".github/workflows/automation-health.yml",
                "state": workflow_state,
            }]}
        if path.endswith("/actions/runs?branch=main&per_page=50"):
            return {"workflow_runs": main_runs}
        if path.endswith("/actions/workflows/7/runs?per_page=20"):
            return {"workflow_runs": schedule_runs}
        if "/actions/runs/" in path and path.endswith("/jobs?per_page=100"):
            return {"jobs": jobs.get(int(path.split("/actions/runs/")[1].split("/")[0]), [])}
        raise AssertionError("Unexpected API path")

    return read


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload


class HealthMonitorTests(unittest.TestCase):
    def test_first_schedule_is_pending_not_failed(self):
        report = snapshot(REPO, reader_for(), now=NOW, current_run_id="9")
        self.assertEqual(report["status"], "baseline_pending")
        self.assertEqual(report["schedule_state"], "baseline_pending")
        self.assertEqual(report["issues"], [])
        self.assertIn("First successful scheduled execution", render(report))

    def test_old_schedule_is_degraded(self):
        old = [{
            "id": 8,
            "event": "schedule",
            "status": "completed",
            "created_at": "2026-11-03T00:00:00Z",
            "conclusion": "success",
        }]
        report = snapshot(REPO, reader_for(schedule_runs=old), now=NOW, current_run_id="9")
        self.assertEqual(report["schedule_state"], "stale")
        self.assertIn("scheduled_health_run_stale", report["issues"])

    def test_failed_previous_schedule_is_degraded(self):
        failed = [{
            "id": 8,
            "event": "schedule",
            "status": "completed",
            "created_at": "2026-11-05T11:30:00Z",
            "conclusion": "failure",
        }]
        report = snapshot(REPO, reader_for(schedule_runs=failed), now=NOW, current_run_id="9")
        self.assertEqual(report["schedule_state"], "failed")
        self.assertIn("last_scheduled_health_run_not_successful", report["issues"])

    def test_recent_failure_is_sanitized(self):
        runs = [dict(SUCCESS_RUN), {
            "id": 1,
            "name": "Gateway contracts",
            "status": "completed",
            "conclusion": "failure",
            "created_at": "2026-11-05T11:30:00Z",
            "head_sha": "abcdef0123",
            "html_url": "https://github.com/yarsalam/ai-packs/actions/runs/1",
        }]
        report = snapshot(REPO, reader_for(main_runs=runs), now=NOW, current_run_id="9")
        self.assertEqual(report["status"], "degraded")
        output = render(report)
        self.assertIn("Gateway contracts", output)
        self.assertNotIn("logs_url", output)
        self.assertNotIn("Authorization", output)

    def test_old_queued_job_is_detected(self):
        runs = [{
            "id": 2,
            "name": "Gateway",
            "status": "queued",
            "created_at": "2026-11-05T10:00:00Z",
            "head_sha": "123456789",
            "html_url": "https://github.com/yarsalam/ai-packs/actions/runs/2",
        }, SUCCESS_RUN]
        jobs = {2: [{
            "name": "matrix",
            "status": "queued",
            "created_at": "2026-11-05T10:00:00Z",
        }]}
        report = snapshot(REPO, reader_for(main_runs=runs, jobs=jobs), now=NOW, current_run_id="9")
        self.assertEqual(report["stale_jobs"][0]["minutes"], 120)
        self.assertIn("stale_jobs_detected", report["issues"])

    def test_current_scheduled_run_is_not_used_as_previous_baseline(self):
        current = [{
            "id": 9,
            "event": "schedule",
            "created_at": "2026-11-05T12:00:00Z",
            "conclusion": None,
        }]
        report = snapshot(REPO, reader_for(schedule_runs=current), now=NOW, current_run_id="9")
        self.assertEqual(report["schedule_state"], "baseline_pending")
        self.assertIsNone(report["previous_schedule"])

    def test_disabled_workflow_is_reported_as_degraded(self):
        report = snapshot(REPO, reader_for(workflow_state="disabled_manually"), now=NOW)
        self.assertIn("inactive_workflows_detected", report["issues"])
        self.assertEqual(report["status"], "degraded")

    def test_stale_last_successful_main_run_is_reported(self):
        old_success = dict(SUCCESS_RUN, created_at="2026-11-03T00:00:00Z")
        report = snapshot(REPO, reader_for(main_runs=[old_success]), now=NOW)
        self.assertEqual(report["last_success_state"], "stale")
        self.assertIn("last_successful_main_run_stale", report["issues"])

    def test_transient_http_errors_retry_then_succeed(self):
        calls, delays = [], []

        def opener(request, timeout):
            calls.append(timeout)
            if len(calls) < 3:
                raise HTTPError(request.full_url, 503, "unavailable", None, None)
            return FakeResponse(b'{"ok": true}')

        result = get_json(
            "https://api.github.com",
            "test-token",
            "/repos/yarsalam/ai-packs",
            opener=opener,
            sleeper=delays.append,
        )
        self.assertEqual(result, {"ok": True})
        self.assertEqual(len(calls), 3)
        self.assertEqual(delays, [1, 2])

    def test_permanent_http_error_is_not_retried(self):
        calls, delays = [], []

        def opener(request, timeout):
            calls.append(timeout)
            raise HTTPError(request.full_url, 403, "forbidden", None, None)

        with self.assertRaisesRegex(RuntimeError, "details redacted"):
            get_json(
                "https://api.github.com",
                "test-token",
                "/repos/yarsalam/ai-packs",
                opener=opener,
                sleeper=delays.append,
            )
        self.assertEqual(len(calls), 1)
        self.assertEqual(delays, [])

    def test_http_error_response_is_closed(self):
        errors = []

        def opener(request, timeout):
            error = HTTPError(request.full_url, 403, "forbidden", None, None)
            errors.append(error)
            raise error

        with self.assertRaisesRegex(RuntimeError, "details redacted"):
            get_json(
                "https://api.github.com",
                "test-token",
                "/repos/yarsalam/ai-packs",
                opener=opener,
                sleeper=lambda _delay: None,
            )

        self.assertEqual(len(errors), 1)
        self.assertTrue(errors[0].fp.closed)

    def test_transient_retry_limit_is_bounded(self):
        calls, delays = [], []

        def opener(request, timeout):
            calls.append(timeout)
            raise HTTPError(request.full_url, 503, "unavailable", None, None)

        with self.assertRaisesRegex(RuntimeError, "retry limit reached|details redacted"):
            get_json(
                "https://api.github.com",
                "test-token",
                "/repos/yarsalam/ai-packs",
                opener=opener,
                sleeper=delays.append,
            )
        self.assertEqual(len(calls), 3)
        self.assertEqual(delays, [1, 2])


if __name__ == "__main__":
    unittest.main()
