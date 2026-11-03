"""Tenant-configurable decision policy for the commercial Safety Pack.

This module deliberately does not claim model accuracy. It turns the upstream
moderation signal into an explicit allow/review/block workflow and supports
customer-owned phrase rules without persisting submitted user content.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any

DEFAULT_POLICY: dict[str, Any] = {
    "version": 1,
    "default_action": "review",
    "category_actions": {
        "external_contact": "review",
        "commercial_spam": "review",
        "violence": "review",
        "semantic_violation": "review",
        "policy_violation": "review",
        "text_length": "block",
        "unknown": "review",
    },
    "blocked_terms": [],
    "review_terms": [],
}

ALLOWED_ACTIONS = {"allow", "review", "block"}
ALLOWED_CATEGORIES = set(DEFAULT_POLICY["category_actions"])
_EXTERNAL_CONTACT = {"تلگرام", "واتساپ", "اینستاگرام", "telegram", "whatsapp", "instagram", "t.me", "@"}
_COMMERCIAL_SPAM = {"خرید", "فروش", "قیمت", "تومان", "ریال", "خریدوفروش", "buy", "sell", "price"}
_DIGIT_TRANSLATION = str.maketrans({
    "۰": "0", "۱": "1", "۲": "2", "۳": "3", "۴": "4",
    "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9",
    "٠": "0", "١": "1", "٢": "2", "٣": "3", "٤": "4",
    "٥": "5", "٦": "6", "٧": "7", "٨": "8", "٩": "9",
})


def normalize_persian(value: str) -> str:
    """Normalize common Persian/Arabic variants for matching, not translation."""
    value = unicodedata.normalize("NFKC", value).casefold()
    value = value.translate(_DIGIT_TRANSLATION)
    value = value.replace("ي", "ی").replace("ى", "ی").replace("ك", "ک")
    value = re.sub(r"[\u200b-\u200f\ufeff]", "", value)
    value = value.replace("ـ", "")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _clean_terms(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or len(value) > 100:
        raise ValueError(f"{field} must be a list containing at most 100 terms")
    terms: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{field} entries must be strings")
        term = normalize_persian(item)
        if len(term) < 2 or len(term) > 80 or any(ord(ch) < 32 for ch in term):
            raise ValueError(f"{field} entries must contain 2 to 80 printable characters")
        terms.append(term)
    return sorted(set(terms))


def normalize_policy(payload: Any) -> dict[str, Any]:
    """Validate and normalize a tenant-owned policy object."""
    if not isinstance(payload, dict):
        raise ValueError("policy must be a JSON object")

    unknown_keys = set(payload) - {"version", "default_action", "category_actions", "blocked_terms", "review_terms"}
    if unknown_keys:
        raise ValueError(f"unsupported policy fields: {', '.join(sorted(unknown_keys))}")

    if payload.get("version", 1) != 1:
        raise ValueError("unsupported policy version")
    default_action = payload.get("default_action", DEFAULT_POLICY["default_action"])
    if default_action not in ALLOWED_ACTIONS:
        raise ValueError("default_action must be allow, review, or block")

    category_actions = dict(DEFAULT_POLICY["category_actions"])
    supplied_actions = payload.get("category_actions", {})
    if not isinstance(supplied_actions, dict):
        raise ValueError("category_actions must be a JSON object")
    for category, action in supplied_actions.items():
        if category not in ALLOWED_CATEGORIES:
            raise ValueError(f"unsupported moderation category: {category}")
        if action not in ALLOWED_ACTIONS:
            raise ValueError(f"invalid action for category {category}")
        category_actions[category] = action

    return {
        "version": 1,
        "default_action": default_action,
        "category_actions": category_actions,
        "blocked_terms": _clean_terms(payload.get("blocked_terms", []), "blocked_terms"),
        "review_terms": _clean_terms(payload.get("review_terms", []), "review_terms"),
    }



def aggregate_metrics(raw: dict[str, Any]) -> dict[str, Any]:
    """Convert Redis category:action counters into a privacy-safe summary."""
    actions = {"allow": 0, "review": 0, "block": 0}
    categories: dict[str, dict[str, int]] = {}
    for key, value in raw.items():
        try:
            category, action = str(key).rsplit(":", 1)
            count = max(0, int(value))
        except (ValueError, TypeError):
            continue
        if action not in ALLOWED_ACTIONS or not category:
            continue
        actions[action] += count
        categories.setdefault(category, {"allow": 0, "review": 0, "block": 0})
        categories[category][action] += count
    return {
        "total": sum(actions.values()),
        "actions": actions,
        "categories": {
            category: {
                **counts,
                "total": sum(counts.values()),
            }
            for category, counts in sorted(categories.items())
        },
    }

def decide_moderation(text: str, upstream: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    """Apply tenant policy to a model/rule signal; uncertain failures go to review."""
    normalized_text = normalize_persian(text)
    blocked_match = next((term for term in policy["blocked_terms"] if term in normalized_text), None)
    review_match = next((term for term in policy["review_terms"] if term in normalized_text), None)

    if blocked_match:
        category, reason, evidence = "custom_blocked_term", "tenant_blocked_term", blocked_match
        action = "block"
    elif review_match:
        category, reason, evidence = "custom_review_term", "tenant_review_term", review_match
        action = "review"
    else:
        reason = str(upstream.get("reason") or "unknown")
        matched = normalize_persian(str(upstream.get("matched") or upstream.get("matched_exemplar") or ""))
        # Fail-safe metadata always takes precedence over a contradictory
        # upstream "allowed" flag. A semantic dependency outage must never
        # become an automatic approval, even if upstream fields disagree.
        if reason == "semantic_check_unavailable" or upstream.get("review_required"):
            category, action = "semantic_unavailable", "review"
            evidence = matched or None
        elif upstream.get("allowed", False):
            category, reason, evidence, action = "clean", None, None, "allow"
        elif reason == "violence_keyword":
            category = "violence"
            action = policy["category_actions"].get(category, policy["default_action"])
        elif reason == "semantic_violation":
            category = "semantic_violation"
            action = policy["category_actions"].get(category, policy["default_action"])
        elif reason == "text_too_long":
            category = "text_length"
            action = policy["category_actions"].get(category, policy["default_action"])
        elif reason == "banned_keyword":
            if matched in _EXTERNAL_CONTACT or any(term in matched for term in _EXTERNAL_CONTACT):
                category = "external_contact"
            elif matched in _COMMERCIAL_SPAM or any(term in matched for term in _COMMERCIAL_SPAM):
                category = "commercial_spam"
            else:
                category = "policy_violation"
            action = policy["category_actions"].get(category, policy["default_action"])
        else:
            category = "unknown"
            action = policy["category_actions"].get(category, policy["default_action"])
        evidence = matched or None

    return {
        "action": action,
        "allowed": action == "allow",
        "review_required": action == "review",
        "blocked": action == "block",
        "category": category,
        "reason": reason,
        "evidence": evidence,
        "policy_version": policy.get("version", 1),
        "model_signal": {
            "layer": upstream.get("layer"),
            "confidence": upstream.get("confidence"),
            "reason": upstream.get("reason"),
        },
    }
