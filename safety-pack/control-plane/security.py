"""Dependency-free API-key primitives for the Safety Pack control plane."""
from __future__ import annotations
import hashlib
import hmac
import secrets
from dataclasses import dataclass

KEY_PREFIX = "spk"
_SECRET_BYTES = 32

@dataclass(frozen=True)
class IssuedApiKey:
    raw_key: str
    prefix: str
    digest: str

def issue_api_key(pepper: str) -> IssuedApiKey:
    """Create a random API key and its database-safe digest."""
    if not isinstance(pepper, str) or len(pepper) < 32:
        raise ValueError("SAFETY_API_KEY_PEPPER must contain at least 32 characters")
    prefix = secrets.token_hex(6)
    secret = secrets.token_urlsafe(_SECRET_BYTES)
    raw_key = f"{KEY_PREFIX}_{prefix}.{secret}"
    return IssuedApiKey(raw_key, prefix, hash_api_key(raw_key, pepper))

def hash_api_key(raw_key: str, pepper: str) -> str:
    """Return a stable HMAC-SHA256 digest; never persist raw_key."""
    if not isinstance(pepper, str) or len(pepper) < 32:
        raise ValueError("SAFETY_API_KEY_PEPPER must contain at least 32 characters")
    if not isinstance(raw_key, str) or not raw_key.startswith(f"{KEY_PREFIX}_"):
        raise ValueError("API key format is invalid")
    return hmac.new(pepper.encode(), raw_key.encode(), hashlib.sha256).hexdigest()

def verify_api_key(raw_key: str, expected_digest: str, pepper: str) -> bool:
    """Constant-time comparison against the stored digest."""
    try:
        actual = hash_api_key(raw_key, pepper)
    except ValueError:
        return False
    if not isinstance(expected_digest, str) or len(expected_digest) != 64:
        return False
    return hmac.compare_digest(actual, expected_digest.lower())
