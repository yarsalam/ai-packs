from scripts.build_distributions import PACKS, SERVICE, build_compose, readme_for


def test_aeo_service_exposes_optional_perplexity_configuration():
    env = SERVICE["aeo_tracker"]["env"]
    assert env["OPENAI_API_KEY"] == "${OPENAI_API_KEY:-}"
    assert env["PERPLEXITY_API_KEY"] == "${PERPLEXITY_API_KEY:-}"
    assert env["PERPLEXITY_MODEL"] == "${PERPLEXITY_MODEL:-sonar}"


def test_generated_seo_compose_passes_both_aeo_provider_keys():
    compose = build_compose("seo-pack", PACKS["seo-pack"])
    env = compose["services"]["aeo_tracker"]["environment"]
    assert "OPENAI_API_KEY" in env
    assert "PERPLEXITY_API_KEY" in env
    assert "PERPLEXITY_MODEL" in env


def test_generated_seo_readme_documents_per_engine_rates_and_citations():
    readme = readme_for("seo-pack", PACKS["seo-pack"])
    assert "PERPLEXITY_API_KEY" in readme
    assert "mention_rate_by_engine" in readme
    assert "citations" in readme
