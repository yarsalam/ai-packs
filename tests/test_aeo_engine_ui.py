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
