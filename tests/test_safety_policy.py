from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

MODULE = Path("safety-pack/gateway/policy.py")
SPEC = importlib.util.spec_from_file_location("safety_policy", MODULE)
assert SPEC and SPEC.loader
policy_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(policy_module)

normalize_persian = policy_module.normalize_persian
normalize_policy = policy_module.normalize_policy
decide_moderation = policy_module.decide_moderation


def test_normalizes_persian_arabic_letters_digits_and_invisible_chars():
    assert normalize_persian("  كَ‌تاب ي ۱۲۳  ") == "کَتاب ی 123"


def test_tenant_blocked_term_overrides_clean_model_signal():
    policy = normalize_policy({"blocked_terms": ["کلمه ممنوع"]})
    result = decide_moderation("این یک کلمه ممنوع است", {"allowed": True}, policy)
    assert result["action"] == "block"
    assert result["blocked"] is True
    assert result["category"] == "custom_blocked_term"


def test_tenant_review_term_routes_to_human_review():
    policy = normalize_policy({"review_terms": ["شاید بررسی شود"]})
    result = decide_moderation("این متن شاید بررسی شود", {"allowed": True}, policy)
    assert result["action"] == "review"
    assert result["review_required"] is True


def test_clean_content_is_allowed():
    policy = normalize_policy({})
    result = decide_moderation("سلام، روز خوبی داشته باشید", {"allowed": True}, policy)
    assert result["action"] == "allow"
    assert result["category"] == "clean"


def test_violence_action_is_customer_configurable():
    policy = normalize_policy({"category_actions": {"violence": "block"}})
    result = decide_moderation(
        "تهدید", {"allowed": False, "reason": "violence_keyword", "matched": "تهدید"},
        policy,
    )
    assert result["action"] == "block"
    assert result["category"] == "violence"


def test_external_contact_rule_defaults_to_review_not_silent_allow():
    policy = normalize_policy({})
    result = decide_moderation(
        "بیا تلگرام", {"allowed": False, "reason": "banned_keyword", "matched": "تلگرام"},
        policy,
    )
    assert result["action"] == "review"
    assert result["category"] == "external_contact"


def test_semantic_dependency_failure_always_routes_to_review():
    policy = normalize_policy({"default_action": "block"})
    result = decide_moderation(
        "متن", {
            "allowed": False, "reason": "semantic_check_unavailable",
            "review_required": True, "confidence": 0.0,
        }, policy,
    )
    assert result["action"] == "review"
    assert result["review_required"] is True


def test_policy_rejects_unknown_categories_and_unbounded_terms():
    with pytest.raises(ValueError):
        normalize_policy({"category_actions": {"everything": "block"}})
    with pytest.raises(ValueError):
        normalize_policy({"blocked_terms": ["x"]})
    with pytest.raises(ValueError):
        normalize_policy({"review_terms": ["a" * 81]})
    with pytest.raises(ValueError):
        normalize_policy({"blocked_terms": ["valid"] * 101})


def test_serialized_policy_can_be_validated_again():
    policy = normalize_policy({
        "category_actions": {"commercial_spam": "block"},
        "review_terms": ["عبارت نمونه"],
    })
    # The API persists this complete object, including version.
    restored = normalize_policy(policy)
    assert restored == policy
