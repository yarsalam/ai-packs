from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "seo-pack/wordpress-plugin/seo-pack/includes/class-api-client.php"
DEMO = ROOT / "seo-pack/wordpress-plugin/seo-pack/admin/class-demo-page.php"


def test_aeo_client_supports_explicit_engine_selection():
    source = CLIENT.read_text(encoding="utf-8")
    assert "array $engines = []" in source
    assert "$payload['engines'] = array_values(array_unique" in source
    assert "['openai', 'perplexity']" in source


def test_aeo_wordpress_demo_defaults_to_configured_engines_and_can_select_one():
    source = DEMO.read_text(encoding="utf-8")
    assert 'id="aeo-all-engines" checked' in source
    assert 'value="openai" class="aeo-engine-option"' in source
    assert 'value="perplexity" class="aeo-engine-option"' in source
    assert "payload.engines = Array.from" in source
    assert "check_aeo_mentions($payload['brand'] ?? '', $payload['prompts'] ?? [], $payload['engines'] ?? [])" in source
    assert "OpenAI و Perplexity" in source
    assert "ChatGPT/Gemini" not in source


def test_aeo_client_preserves_structured_unavailable_response():
    source = CLIENT.read_text(encoding="utf-8")
    assert "bool $allowUnavailable = false" in source
    assert "$allowUnavailable && $code === 503" in source
    assert "($data['status'] ?? '') === 'unavailable'" in source
    assert "check-mentions', $payload, true" in source


def test_aeo_demo_renders_per_engine_status_and_safe_citation_links():
    source = DEMO.read_text(encoding="utf-8")
    assert "function renderAeoResult(container, data)" in source
    assert "mention_rate_by_engine" in source
    assert "item.mentioned === null" in source or "item.mentioned === true" in source
    assert "item.citations" in source
    assert "new URL(rawUrl)" in source
    assert "noopener noreferrer" in source
    assert "این وضعیت به معنی عدم ذکر برند نیست" in source


def test_backlink_graph_metric_is_not_mislabeled_as_vendor_trust_flow():
    source = DEMO.read_text(encoding="utf-8")
    assert "شاخص داخلی" in source
    assert "Trust Flow رسمی Majestic" in source
    assert "امتیاز دامنهٔ مستقل" in source
