from scripts.smoke_test_packs import TEST_SITE_DOMAIN, add_result, license_headers


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
