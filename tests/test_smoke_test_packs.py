from scripts.smoke_test_packs import TEST_SITE_DOMAIN, add_result, license_headers, validate_payload


def test_smoke_test_license_headers_include_exact_bound_domain():
    assert license_headers("temporary-key") == {
        "X-License-Key": "temporary-key",
        "X-Site-Domain": TEST_SITE_DOMAIN,
    }
    assert TEST_SITE_DOMAIN == "smoke-test.local"


def test_degraded_health_can_be_recorded_as_warning():
    results = []
    add_result(
        results,
        "gateway health",
        ok=False,
        status=200,
        elapsed_ms=12,
        detail='{"status":"degraded"}',
        status_override="WARN",
    )
    assert results[0]["status"] == "WARN"


def test_matching_smoke_rejects_candidates_outside_caller_allowlist():
    payload = {"candidates": [2, 3]}
    valid = {
        "status": "ok",
        "recommendations": [{
            "user_id": 2,
            "score": 0.71,
            "score_components": {"embedding": 0.71},
        }],
    }
    ok, _ = validate_payload("recommendations", valid, payload)
    assert ok is True

    invalid = {
        "status": "ok",
        "recommendations": [{
            "user_id": 99,
            "score": 0.99,
            "score_components": {"embedding": 0.99},
        }],
    }
    ok, _ = validate_payload("recommendations", invalid, payload)
    assert ok is False


def test_matching_smoke_accepts_explicit_unavailable_score_not_fabricated_value():
    ok, _ = validate_payload(
        "unavailable_score",
        {"detail": "Match score unavailable: valid embeddings are required for both entities"},
    )
    assert ok is True


def test_license_domain_mismatch_is_detected():
    headers = license_headers("temporary-key", "wrong-domain.example")
    assert headers["X-Site-Domain"] == "wrong-domain.example"
    ok, _ = validate_payload(
        "domain_mismatch",
        {"detail": "License key is not authorized for this site domain"},
    )
    assert ok is True
    ok, _ = validate_payload("domain_mismatch", {"detail": "some other error"})
    assert ok is False
