"""Contract tests for shared licensing behavior across the four AI Pack gateways.

Run with GATEWAY_MODULE_PATH=seo-pack/gateway/main.py pytest -q tests/test_gateway_contract.py
"""
import asyncio
import importlib.util
import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.requests import Request


@pytest.fixture(scope="module")
def gateway():
    path = Path(os.environ["GATEWAY_MODULE_PATH"])
    spec = importlib.util.spec_from_file_location("gateway_under_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeRedis:
    def __init__(self, values=None):
        self.values = values or {}
        self.counter = 0
        self.expiry_calls = []

    async def get(self, key):
        return self.values.get(key)

    async def incr(self, _key):
        self.counter += 1
        return self.counter

    async def expire(self, key, seconds):
        self.expiry_calls.append((key, seconds))
        return True

    async def ping(self):
        return True

    async def aclose(self):
        return None


def _license_key_hash(gateway, key):
    hash_fn = getattr(gateway, "_hash_key", None) or getattr(gateway, "_hash")
    return hash_fn(key)


def _fake_redis_for(gateway, key, **overrides):
    record = {
        "domain": "customer.example",
        "plan": "pro",
        "expires": "2099-12-31",
        "active": True,
    }
    record.update(overrides)
    redis_key = f"{gateway.LICENSE_PREFIX}{_license_key_hash(gateway, key)}"
    return FakeRedis({redis_key: json.dumps(record)})


@pytest.mark.parametrize("raw_date,expected", [
    ("2000-01-01", True),
    ("2099-12-31", False),
])
def test_date_only_expiry(gateway, raw_date, expected):
    assert gateway._license_is_expired(raw_date) is expected


def test_date_only_expiry_is_valid_for_the_current_utc_day(gateway):
    today_utc = datetime.now(timezone.utc).date().isoformat()
    assert gateway._license_is_expired(today_utc) is False


def test_timestamp_expiry_is_normalized_to_utc(gateway):
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    assert gateway._license_is_expired(past) is True
    assert gateway._license_is_expired(future) is False


def test_invalid_expiry_fails_closed(gateway, monkeypatch):
    key = "test-license-key"
    monkeypatch.setattr(gateway, "redis_client", _fake_redis_for(gateway, key, expires="not-a-date"))
    with pytest.raises(HTTPException) as exc:
        asyncio.run(gateway.validate_license(key))
    assert exc.value.status_code == 403


def test_inactive_license_is_rejected(gateway, monkeypatch):
    key = "test-license-key"
    monkeypatch.setattr(gateway, "redis_client", _fake_redis_for(gateway, key, active=False))
    with pytest.raises(HTTPException) as exc:
        asyncio.run(gateway.validate_license(key))
    assert exc.value.status_code == 403


def test_active_license_is_returned(gateway, monkeypatch):
    key = "test-license-key"
    record = {"active": True, "plan": "pro", "expires": "2099-12-31"}
    monkeypatch.setattr(gateway, "redis_client", _fake_redis_for(gateway, key, **record))
    assert asyncio.run(gateway.validate_license(key))["plan"] == "pro"


def test_license_validation_route_checks_the_actual_key(gateway, monkeypatch):
    key = "test-license-key"
    monkeypatch.setattr(gateway, "redis_client", _fake_redis_for(gateway, key))
    request = SimpleNamespace(headers={"X-License-Key": key})
    response = asyncio.run(gateway.license_status(request))
    assert response["status"] == "active"
    assert response["plan"] == "pro"


def test_license_key_in_query_string_is_not_authentication(gateway, monkeypatch):
    key = "test-license-key"
    monkeypatch.setattr(gateway, "redis_client", _fake_redis_for(gateway, key))
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/protected",
        "raw_path": b"/protected",
        "query_string": b"license_key=test-license-key",
        "headers": [],
        "client": ("testclient", 123),
        "server": ("testserver", 80),
        "root_path": "",
    }
    request = Request(scope)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(gateway.get_license(request))
    assert exc.value.status_code == 401


def test_gateway_refuses_to_start_without_strong_admin_secret(gateway, monkeypatch):
    monkeypatch.setattr(gateway, "ADMIN_TOKEN", "")
    with pytest.raises(RuntimeError, match="ADMIN_TOKEN"):
        asyncio.run(gateway.startup())
