from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PACKS = [
    (
        "seo-pack",
        "seo-pack/wordpress-plugin/seo-pack/includes/class-api-client.php",
        "seo-pack/wordpress-plugin/seo-pack/admin/class-settings-page.php",
        "seo_pack_usage",
        "seo-pack-usage",
        "request",
    ),
    (
        "revenue-pack",
        "revenue-pack/wordpress-plugin/revenue-pack/includes/class-api-client.php",
        "revenue-pack/wordpress-plugin/revenue-pack/admin/class-settings-page.php",
        "revenue_pack_usage",
        "rp-usage",
        "request",
    ),
    (
        "matching-pack",
        "matching-pack/wordpress-plugin/matching-pack/includes/class-api-client.php",
        "matching-pack/wordpress-plugin/matching-pack/admin/class-settings-page.php",
        "matching_pack_usage",
        "mp-usage",
        "request",
    ),
    (
        "safety-pack",
        "safety-pack/wordpress-plugin/safety-pack/includes/class-api-client.php",
        "safety-pack/wordpress-plugin/safety-pack/admin/class-settings-page.php",
        "safety_pack_usage",
        "sp-usage",
        "request_json",
    ),
]


def test_all_pack_api_clients_expose_usage_endpoint():
    for name, client_path, _, _, _, transport in PACKS:
        source = (ROOT / client_path).read_text(encoding="utf-8")
        assert "public function get_usage(): array" in source, name
        assert f"$this->{transport}('GET', '/usage')" in source, name


def test_all_pack_usage_ajax_endpoints_are_nonce_and_capability_checked():
    for name, _, settings_path, action, _, _ in PACKS:
        source = (ROOT / settings_path).read_text(encoding="utf-8")
        assert f"wp_ajax_{action}" in source, name
        assert "public function ajax_usage(): void" in source, name
        assert "check_ajax_referer(" in source, name
        assert "current_user_can('manage_options')" in source, name
        assert "wp_send_json_success($usage)" in source, name
        assert "wp_send_json_error(['message' => $usage['error']], 502)" in source, name


def test_all_pack_settings_pages_render_usage_loading_error_and_live_states():
    for name, _, settings_path, _, element_id, _ in PACKS:
        source = (ROOT / settings_path).read_text(encoding="utf-8")
        assert f'id="{element_id}-btn"' in source, name
        assert f'id="{element_id}-result"' in source, name
        assert 'aria-live="polite"' in source, name
        assert "در حال دریافت اطلاعات مصرف از Gateway" in source, name
        assert "خطا در دریافت سهمیه" in source, name
        assert "replaceChildren()" in source, name


def test_seo_connection_response_is_rendered_as_text_not_html():
    source = (
        ROOT
        / "seo-pack/wordpress-plugin/seo-pack/admin/class-settings-page.php"
    ).read_text(encoding="utf-8")
    assert "result.innerHTML" not in source
    assert "pre.textContent = JSON.stringify(data, null, 2)" in source
    assert "result.replaceChildren(pre)" in source


def test_all_pack_usage_panels_fail_closed_on_incomplete_counters():
    for name, _, settings_path, _, _, _ in PACKS:
        source = (ROOT / settings_path).read_text(encoding="utf-8")
        assert "const readNonNegative = function (value)" in source, name
        assert "readNonNegative(period.used) === null" in source, name
        assert "readNonNegative(period.limit) === null" in source, name
        assert "readNonNegative(period.remaining) === null" in source, name
        assert "Number(period.used || 0)" not in source, name
        assert "Number(period.limit || 0)" not in source, name
        assert "Number(period.remaining || 0)" not in source, name


def test_usage_weight_labels_include_seo_remote_url_audit():
    for name, _, settings_path, _, _, _ in PACKS:
        source = (ROOT / settings_path).read_text(encoding="utf-8")
        assert "remote_url_audit: 'ممیزی URL از راه دور'" in source, name
