"""
SEO Pack Gateway
================
یه FastAPI که جلوی ۴ سرویس SEO می‌ایسته:
  - ai_seo          :8021  → /seo/*
  - aeo_tracker     :8030  → /aeo/*
  - ai_backlink     :8032  → /backlink/*
  - ai_recommender  :8033  → /recommend/*

هر request اول License Key رو چک می‌کنه، بعد به سرویس مربوطه پروکسی می‌کنه.
"""

import os
import secrets
import hashlib
import httpx
from datetime import datetime, date, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import redis.asyncio as aioredis

# ── Config ─────────────────────────────────────────────────────────────────
SERVICES = {
    "seo":       os.getenv("AI_SEO_URL",         "http://ai_seo:8021"),
    "aeo":       os.getenv("AEO_TRACKER_URL",    "http://aeo_tracker:8030"),
    "backlink":  os.getenv("AI_BACKLINK_URL",    "http://ai_backlink_quality:8032"),
    "recommend": os.getenv("AI_RECOMMENDER_URL", "http://ai_seo_recommender:8033"),
}

REDIS_URL   = os.getenv("REDIS_URL", "redis://redis:6379/0")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

# License keys در Redis ذخیره می‌شن با این prefix
# key:  license:{key_hash}
# value: JSON  {"domain": "example.com", "plan": "pro", "expires": "2026-12-31", "active": true}
LICENSE_PREFIX = "license:"
RATE_LIMIT_PREFIX = "ratelimit:"
RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "500"))

# Billable usage credits are provisional defaults; adjust after measuring inference cost.
PLAN_LIMITS = {
    "free": {"hourly_units": 60, "monthly_units": 1000},
    "basic": {"hourly_units": min(200, RATE_LIMIT_PER_HOUR), "monthly_units": 5000},
    "pro": {"hourly_units": RATE_LIMIT_PER_HOUR, "monthly_units": 50000},
    "enterprise": {"hourly_units": RATE_LIMIT_PER_HOUR * 5, "monthly_units": 250000},
}
USAGE_PREFIX = "seo_usage:"
TRAINING_PATHS = {
    "/recommend/train", "/monetization/retrain", "/revenue/train",
    "/uplift/train", "/feedback/train", "/feedback/train/batch",
}

app = FastAPI(
    title="SEO Pack Gateway",
    version="1.0.0",
    description="Unified gateway for ai_seo, aeo_tracker, ai_backlink_quality, ai_seo_recommender",
)

redis_client: Optional[aioredis.Redis] = None


# ── Startup ─────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    global redis_client
    if len(ADMIN_TOKEN) < 32:
        raise RuntimeError("ADMIN_TOKEN must be set to a random secret of at least 32 characters")
    redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    await redis_client.ping()


@app.on_event("shutdown")
async def shutdown():
    if redis_client:
        await redis_client.aclose()


# ── License Helpers ──────────────────────────────────────────────────────────
def _hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def _license_is_expired(value: str) -> bool:
    """Accept date-only expiries through the end of that UTC date; normalize timestamps to UTC."""
    try:
        if len(value) == 10:
            return datetime.now(timezone.utc).date() > date.fromisoformat(value)
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > parsed.astimezone(timezone.utc)
    except (TypeError, ValueError):
        raise HTTPException(403, "License expiry is invalid")


async def validate_license(license_key: str) -> dict:
    """
    License key رو چک می‌کنه.
    Returns: dict با اطلاعات license
    Raises: HTTPException اگه نامعتبر باشه
    """
    if not license_key:
        raise HTTPException(401, "License key الزامی است")

    key_hash = _hash_key(license_key)
    data = await redis_client.get(f"{LICENSE_PREFIX}{key_hash}")

    if not data:
        raise HTTPException(403, "License key نامعتبر است")

    import json
    info = json.loads(data)

    if not info.get("active", False):
        raise HTTPException(403, "License key غیرفعال است")

    expires = info.get("expires")
    if expires and _license_is_expired(expires):
        raise HTTPException(403, "License key منقضی شده است")
    plan = str(info.get("plan", "basic")).lower()
    if plan not in PLAN_LIMITS:
        raise HTTPException(403, "License plan is not supported")
    info["plan"] = plan
    return info
async def _usage_weight(path: str) -> int:
    if path in TRAINING_PATHS:
        return 20
    if path == "/verify/face" or path.startswith("/image/"):
        return 10
    if path.endswith("/batch"):
        return 5
    if path.startswith("/personality/") or path.startswith("/assistant/") or path.startswith("/match/"):
        return 2
    if path.startswith("/seo/") or path.startswith("/aeo/") or path.startswith("/backlink/") or path.startswith("/recommend/"):
        return 2
    return 1


async def _meter_usage(license_key: str, info: dict, path: str) -> None:
    plan = info.get("plan", "basic")
    limits = PLAN_LIMITS[plan]
    if path in TRAINING_PATHS and plan not in ("pro", "enterprise"):
        raise HTTPException(403, "Model training requires a Pro or Enterprise plan")

    key_hash = _hash_key(license_key) if "_hash_key" in globals() else _hash(license_key)
    weight = await _usage_weight(path)
    now = datetime.now(timezone.utc)
    hour_key = f"{RATE_LIMIT_PREFIX}{key_hash}:hour"
    month_key = f"{USAGE_PREFIX}{key_hash}:{now:%Y-%m}"

    hourly_units = await redis_client.incrby(hour_key, weight)
    if hourly_units == weight:
        await redis_client.expire(hour_key, 3600)

    monthly_units = await redis_client.incrby(month_key, weight)
    if monthly_units == weight:
        if now.month == 12:
            next_month = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            next_month = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
        ttl = max(3600, int((next_month - now).total_seconds()) + 86400)
        await redis_client.expire(month_key, ttl)

    if hourly_units > limits["hourly_units"]:
        raise HTTPException(429, f"Hourly usage quota exceeded for plan '{plan}'")
    if monthly_units > limits["monthly_units"]:
        raise HTTPException(429, f"Monthly usage quota exceeded for plan '{plan}'")


async def _usage_snapshot(license_key: str, info: dict) -> dict:
    plan = info.get("plan", "basic")
    limits = PLAN_LIMITS[plan]
    key_hash = _hash_key(license_key) if "_hash_key" in globals() else _hash(license_key)
    now = datetime.now(timezone.utc)
    hourly = await redis_client.get(f"{RATE_LIMIT_PREFIX}{key_hash}:hour")
    monthly = await redis_client.get(f"{USAGE_PREFIX}{key_hash}:{now:%Y-%m}")
    hourly_used = int(hourly or 0)
    monthly_used = int(monthly or 0)
    return {
        "plan": plan,
        "usage_unit": "credits",
        "hourly": {
            "used": hourly_used,
            "limit": limits["hourly_units"],
            "remaining": max(0, limits["hourly_units"] - hourly_used),
        },
        "monthly": {
            "used": monthly_used,
            "limit": limits["monthly_units"],
            "remaining": max(0, limits["monthly_units"] - monthly_used),
            "period": now.strftime("%Y-%m"),
        },
        "weights": {
            "ordinary_request": 1,
            "text_analysis_or_recommendation": 2,
            "batch_request": 5,
            "image_or_face_verification": 10,
            "model_training": 20,
        },
    }


async def get_license(request: Request) -> dict:
    key = request.headers.get("X-License-Key")
    info = await validate_license(key)
    await _meter_usage(key, info, request.url.path)
    return info


# ── Generic Proxy ────────────────────────────────────────────────────────────
async def _proxy(service: str, path: str, request: Request) -> JSONResponse:
    base_url = SERVICES[service]
    url = f"{base_url}/{path.lstrip('/')}"

    body = await request.body()
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ("host", "x-license-key", "content-length")
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.request(
                method=request.method,
                url=url,
                content=body,
                headers=headers,
                params=dict(request.query_params),
            )
    except httpx.TimeoutException as exc:
        raise HTTPException(504, "Upstream service timed out") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(502, "Upstream service unavailable") from exc

    return JSONResponse(
        content=resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"raw": resp.text},
        status_code=resp.status_code,
    )


# ── SEO Routes (ai_seo :8021) ─────────────────────────────────────────────
@app.post("/seo/predict/traffic", tags=["SEO"])
async def seo_predict_traffic(request: Request, _: dict = Depends(get_license)):
    """پیش‌بینی ترافیک آینده بر اساس داده‌های تاریخی"""
    return await _proxy("seo", "/predict/traffic", request)


@app.post("/seo/feedback/campaign", tags=["SEO"])
async def seo_campaign_feedback(request: Request, _: dict = Depends(get_license)):
    """ارسال فیدبک کمپین برای self-learning"""
    return await _proxy("seo", "/feedback/campaign", request)


# ── AEO Routes (aeo_tracker :8030) ───────────────────────────────────────
@app.post("/aeo/check-mentions", tags=["AEO"])
async def aeo_check_mentions(request: Request, _: dict = Depends(get_license)):
    """چک کردن اینکه برند در پاسخ‌های AI ذکر می‌شه یا نه"""
    return await _proxy("aeo", "/check-mentions", request)


@app.get("/aeo/history/{brand}", tags=["AEO"])
async def aeo_history(brand: str, request: Request, _: dict = Depends(get_license)):
    """تاریخچه mention های یه برند"""
    return await _proxy("aeo", f"/history/{brand}", request)


# ── Backlink Routes (ai_backlink_quality :8032) ───────────────────────────
@app.post("/backlink/trust-flow", tags=["Backlink"])
async def backlink_trust_flow(request: Request, _: dict = Depends(get_license)):
    """محاسبه Trust Flow برای شبکه لینک‌ها"""
    return await _proxy("backlink", "/trust-flow", request)


@app.post("/backlink/topic-similarity", tags=["Backlink"])
async def backlink_topic_similarity(request: Request, _: dict = Depends(get_license)):
    """شباهت موضوعی دو صفحه برای ارزیابی کیفیت بک‌لینک"""
    return await _proxy("backlink", "/topic-similarity", request)


# ── Recommender Routes (ai_seo_recommender :8033) ────────────────────────
@app.post("/recommend/train", tags=["Recommender"])
async def recommender_train(request: Request, _: dict = Depends(get_license)):
    """آموزش مدل collaborative filtering با داده‌های interaction"""
    return await _proxy("recommend", "/train", request)


@app.post("/recommend/recommend", tags=["Recommender"])
async def recommender_recommend(request: Request, _: dict = Depends(get_license)):
    """دریافت پیشنهادات SEO شخصی‌سازی‌شده برای یه کاربر"""
    return await _proxy("recommend", "/recommend", request)


# ── Admin: License Management ─────────────────────────────────────────────
@app.post("/admin/license/create", tags=["Admin"])
async def create_license(request: Request):
    """
    ساختن license key جدید
    Header: X-Admin-Token
    Body: {"domain": "example.com", "plan": "pro", "expires": "2026-12-31"}
    """
    admin_token = request.headers.get("X-Admin-Token")
    if not admin_token or not secrets.compare_digest(admin_token, ADMIN_TOKEN):
        raise HTTPException(403, "Admin token نامعتبر است")

    import json, secrets
    body = await request.json()
    plan = str(body.get("plan", "basic")).lower()
    if plan not in PLAN_LIMITS:
        raise HTTPException(422, "Unsupported plan. Choose free, basic, pro, or enterprise.")
    expires = body.get("expires", "2099-12-31")
    if not isinstance(expires, str) or not expires.strip():
        raise HTTPException(422, "License expiry is required")
    try:
        expired = bool(expires) and _license_is_expired(str(expires))
    except HTTPException as exc:
        raise HTTPException(422, "Invalid license expiry; use YYYY-MM-DD or ISO timestamp") from exc
    if expired:
        raise HTTPException(422, "License expiry must be in the future")
    raw_key = secrets.token_urlsafe(32)
    key_hash = _hash_key(raw_key)
    info = {
        "domain":  body.get("domain", "*"),
        "plan":    plan,
        "expires": expires,
        "active":  True,
        "created": datetime.now().isoformat(),
    }
    await redis_client.set(f"{LICENSE_PREFIX}{key_hash}", json.dumps(info))

    return {
        "license_key": raw_key,   # فقط یه بار نشون داده می‌شه
        "key_hash":    key_hash,
        **info,
    }


@app.delete("/admin/license/{key_hash}", tags=["Admin"])
async def revoke_license(key_hash: str, request: Request):
    """غیرفعال کردن یه license"""
    admin_token = request.headers.get("X-Admin-Token")
    if not admin_token or not secrets.compare_digest(admin_token, ADMIN_TOKEN):
        raise HTTPException(403, "Admin token نامعتبر است")

    import json
    data = await redis_client.get(f"{LICENSE_PREFIX}{key_hash}")
    if not data:
        raise HTTPException(404, "License پیدا نشد")

    info = json.loads(data)
    info["active"] = False
    await redis_client.set(f"{LICENSE_PREFIX}{key_hash}", json.dumps(info))
    return {"status": "revoked", "key_hash": key_hash}


# ── Health ───────────────────────────────────────────────────────────────
@app.get("/usage", tags=["Usage"])
async def get_usage(request: Request):
    key = request.headers.get("X-License-Key")
    info = await validate_license(key)
    return await _usage_snapshot(key, info)


@app.get("/license/validate", tags=["License"])
async def license_status(request: Request):
    """Validate the supplied license; deliberately does not consume an API quota unit."""
    info = await validate_license(request.headers.get("X-License-Key"))
    return {
        "status": "active",
        "plan": info.get("plan"),
        "expires": info.get("expires"),
    }


@app.get("/health", tags=["System"])
async def health():
    services_status = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in SERVICES.items():
            try:
                r = await client.get(f"{url}/health")
                try:
                    body = r.json()
                except ValueError:
                    body = {}
                reported = str(body.get("status", "")).lower()
                healthy = r.status_code == 200 and (not reported or reported in {"healthy", "ok", "ready"})
                services_status[name] = "ok" if healthy else "degraded"
            except Exception:
                services_status[name] = "down"

    payload = {
        "status": "healthy" if all(value == "ok" for value in services_status.values()) else ("degraded" if any(value == "ok" for value in services_status.values()) else "unavailable"),
        "gateway": "seo_pack_v1",
        "timestamp": datetime.now().isoformat(),
        "services": services_status,
    }
    return JSONResponse(content=payload, status_code=503 if payload["status"] == "unavailable" else 200)




@app.get("/", tags=["System"])
async def root():
    return {
        "name": "SEO Pack Gateway",
        "version": "1.0.0",
        "endpoints": {
            "seo":       ["/seo/predict/traffic", "/seo/feedback/campaign"],
            "aeo":       ["/aeo/check-mentions", "/aeo/history/{brand}"],
            "backlink":  ["/backlink/trust-flow", "/backlink/topic-similarity"],
            "recommend": ["/recommend/train", "/recommend/recommend"],
        },
        "auth": "X-License-Key header یا ?license_key= query param",
    }
