import unittest
from datetime import datetime, timezone
from scripts.automation_health_check import snapshot, render

NOW = datetime(2026, 11, 5, 12, 0, tzinfo=timezone.utc)
REPO = "yarsalam/ai-packs"

def reader_for(main_runs=None, schedule_runs=None, jobs=None):
    main_runs, schedule_runs, jobs = main_runs or [], schedule_runs or [], jobs or {}
    def read(path):
        if path.endswith("/actions/workflows?per_page=100"):
            return {"workflows":[{"id":7,"name":"Health","path":".github/workflows/automation-health.yml","state":"active"}]}
        if path.endswith("/actions/runs?branch=main&per_page=50"):
            return {"workflow_runs":main_runs}
        if path.endswith("/actions/workflows/7/runs?per_page=20"):
            return {"workflow_runs":schedule_runs}
        if "/actions/runs/" in path and path.endswith("/jobs?per_page=100"):
            return {"jobs":jobs.get(int(path.split("/actions/runs/")[1].split("/")[0]),[])}
        raise AssertionError("Unexpected API path")
    return read

class HealthMonitorTests(unittest.TestCase):
    def test_first_schedule_is_pending_not_failed(self):
        r=snapshot(REPO, reader_for(), now=NOW, current_run_id="9")
        self.assertEqual(r["status"],"baseline_pending")
        self.assertEqual(r["issues"],[])
        self.assertIn("First scheduled execution",render(r))

    def test_old_schedule_is_degraded(self):
        old=[{"id":8,"event":"schedule","created_at":"2026-11-03T00:00:00Z","conclusion":"success"}]
        r=snapshot(REPO, reader_for(schedule_runs=old), now=NOW, current_run_id="9")
        self.assertEqual(r["schedule_state"],"stale")
        self.assertIn("scheduled_health_run_stale",r["issues"])

    def test_recent_failure_is_sanitized(self):
        runs=[{"id":1,"name":"Gateway contracts","status":"completed","conclusion":"failure",
               "created_at":"2026-11-05T11:30:00Z","head_sha":"abcdef0123",
               "html_url":"https://github.com/yarsalam/ai-packs/actions/runs/1"}]
        r=snapshot(REPO,reader_for(main_runs=runs),now=NOW,current_run_id="9")
        self.assertEqual(r["status"],"degraded")
        text=render(r)
        self.assertIn("Gateway contracts",text)
        self.assertNotIn("logs_url",text)
        self.assertNotIn("Authorization",text)

    def test_old_queued_job_is_detected(self):
        runs=[{"id":2,"name":"Gateway","status":"queued","created_at":"2026-11-05T10:00:00Z",
               "head_sha":"123456789","html_url":"https://github.com/yarsalam/ai-packs/actions/runs/2"}]
        jobs={2:[{"name":"matrix","status":"queued","created_at":"2026-11-05T10:00:00Z"}]}
        r=snapshot(REPO,reader_for(main_runs=runs,jobs=jobs),now=NOW,current_run_id="9")
        self.assertEqual(r["stale_jobs"][0]["minutes"],120)
        self.assertIn("stale_jobs_detected",r["issues"])

    def test_current_scheduled_run_is_not_used_as_previous_baseline(self):
        current=[{"id":9,"event":"schedule","created_at":"2026-11-05T12:00:00Z","conclusion":None}]
        r=snapshot(REPO,reader_for(schedule_runs=current),now=NOW,current_run_id="9")
        self.assertEqual(r["schedule_state"],"baseline_pending")
        self.assertIsNone(r["previous_schedule"])

if __name__ == "__main__":
    unittest.main()
