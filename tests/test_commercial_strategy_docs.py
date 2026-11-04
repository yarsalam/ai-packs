from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_product_strategy_covers_all_four_pack_acceptance_criteria():
    strategy = (ROOT / "docs/COMMERCIAL_PRODUCT_STRATEGY.md").read_text(encoding="utf-8")
    for heading in ("SEO Pack", "Revenue Pack", "Matching Pack", "Safety Pack"):
        assert heading in strategy
    for priority in ("P0", "P1", "P2", "P3"):
        assert priority in strategy


def test_competitor_benchmark_contains_official_workflow_evidence():
    benchmark = (ROOT / "docs/COMPETITOR_PRODUCT_BENCHMARK_2026-11-04.md").read_text(encoding="utf-8")
    for source in (
        "semrush.com/kb/1596-visibility-overview-report",
        "revenuecat.com/docs/dashboard-and-metrics/charts/realized-ltv-per-customer-chart",
        "appsflyer.com/products/measurement/incrementality",
        "docs.recombee.com/ab-testing",
        "docs.thehive.ai/docs/handle-appeals",
    ):
        assert source in benchmark
    assert "Gap/acceptance" in benchmark


def test_execution_ledger_records_current_source_pin_and_release_blockers():
    status = (ROOT / "docs/status/COMMERCIALIZATION_STATUS.md").read_text(encoding="utf-8")
    sequence = (ROOT / "docs/COMMERCIAL_EXECUTION_SEQUENCE.md").read_text(encoding="utf-8")
    assert "PR #26" in status
    assert "4344cb05afe461551e1bfdc379b26a3c0fedddd9" in status
    assert "BLOCKED" in status
    assert "Safety #8" in sequence or "Issue #8" in sequence
