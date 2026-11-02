import importlib.util
from pathlib import Path

MODULE = Path("scripts/evaluate_moderation.py")
SPEC = importlib.util.spec_from_file_location("evaluate_moderation", MODULE)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def test_action_metrics_count_false_positives_and_false_negatives():
    rows = [
        {"expected_action": "allow", "predicted_action": "allow"},
        {"expected_action": "allow", "predicted_action": "review"},
        {"expected_action": "block", "predicted_action": "allow"},
        {"expected_action": "review", "predicted_action": "review"},
    ]
    report = module.build_report(rows, [10.0, 20.0, 30.0, 40.0])
    assert report["action_accuracy"] == 0.5
    assert report["flagged_vs_allow"]["fp"] == 1
    assert report["flagged_vs_allow"]["fn"] == 1
    assert report["latency_ms"]["p50"] == 20.0


def test_per_category_metrics_are_aggregated_without_input_text():
    rows = [
        {"expected_action": "review", "predicted_action": "review",
         "expected_category": "external_contact", "predicted_category": "external_contact"},
        {"expected_action": "allow", "predicted_action": "allow",
         "expected_category": "clean", "predicted_category": "clean"},
    ]
    report = module.build_report(rows, [12.0, 13.0])
    assert report["per_category"]["external_contact"]["f1"] == 1.0
    assert "سلام" not in str(report)
    assert report["privacy"].startswith("raw input text is intentionally omitted")


def test_base_url_rejects_localhost_lookalikes_and_remote_http():
    import pytest
    for value in ("http://localhost.evil.test", "http://127.0.0.2", "http://example.com"):
        with pytest.raises(ValueError):
            module.validate_base_url(value)


def test_base_url_allows_https_and_exact_loopback_hosts():
    assert module.validate_base_url("https://safety.example.test").scheme == "https"
    assert module.validate_base_url("http://localhost:9001").hostname == "localhost"
    assert module.validate_base_url("http://127.0.0.1:9001").hostname == "127.0.0.1"


def test_base_url_rejects_embedded_credentials():
    import pytest
    with pytest.raises(ValueError):
        module.validate_base_url("https://user:password@safety.example.test")
