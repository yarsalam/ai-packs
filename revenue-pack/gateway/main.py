"""
Revenue Pack Gateway
====================
جلوی ۴ سرویس Revenue می‌ایسته:
  - ai_monetization  :8015  → /monetization/*   (XGBoost promotion scoring)
  - ai_revenue       :8000  → /revenue/*         (GBM LTV prediction)
  - ai_uplift        :8031  → /uplift/*           (Uplift modeling)
  - ai_feedback      :8004  → /feedback/*         (Conversion trainer)

ویژگی‌های خاص این پک:
  - ai_monetization  به Redis وابسته (feedback buffering + model cache)
  - ai_revenue       model persistence روی volume
  - ai_uplift        fallback mode داره (اگه مدل train نشده باشه avg_uplift برمی‌گردونه)
  - ai_feedback      incremental + batch training — دو حالت دارد
"""

import os, hashlib, json, httpx
from datetime import datetime, date, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import redis.asyncio as aioredis

# ── Config ────────────────────────────────────────────────────────────────────
SERVICES = {
    "monetization": os.getenv("AI_MONETIZATION_URL", "http://ai_monetization:8015"),
    "revenue":      os.getenv("AI_REVENUE_URL",      "http://ai_revenue:8000"),
    "uplift":       os.getenv("AI_UPLIFT_URL",        "http://ai_uplift:8031"),
    "feedback":     os.getenv("AI_FEEDBACK_URL",      "http://ai_feedback:8004"),
}

REDIS_URL           = os.getenv("REDIS_URL",   "redis://redis:6379/0")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
LICENSE_PREFIX      = "revenue_license:"
RATE_LIMIT_PREFIX   = "revenue_ratelimit:"
RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "2000"))

app = FastAPI(
    title="Revenue Pack Gateway",
    version="1.0.0",
    description="Unified gateway for ai_monetization, ai_revenue, ai_uplift, ai_feedback",
)
redis_client: Optional[aioredis.Redis] = None


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


# ── License ───────────────────────────────────────────────────────────────────
def _hash(raw: str) -> str:
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


async def validate_license(key: str) -> dict:
    if not key:
        raise HTTPException(401, "License key الزامی است")
    data = await redis_client.get(f"{LICENSE_PREFIX}{_hash(key)}")
    if not data:
        raise HTTPException(403, "License key نامعتبر است")
    info = json.loads(data)
    if not info.get("active"):
        raise HTTPException(403, "License key غیرفعال است")
    exp = info.get("expires")
    if exp and _license_is_expired(exp):
        raise HTTPException(403, "License key منقضی شده است")
    return info


async def check_rate_limit(key: str):
    rk = f"{RATE_LIMIT_PREFIX}{_hash(key)}"
    count = await redis_client.incr(rk)
    if count == 1:
        await redis_client.expire(rk, 3600)
    if count > RATE_LIMIT_PER_HOUR:
        raise HTTPException(429, f"Rate limit: {RATE_LIMIT_PER_HOUR} req/hour")


async def get_license(request: Request) -> dict:
    key = request.headers.get("X-License-Key")
    info = await validate_license(key)
    await check_rate_limit(key)
    return info


# ── Generic JSON proxy ────────────────────────────────────────────────────────
async def _proxy(service: str, path: str, request: Request) -> JSONResponse:
    url  = f"{SERVICES[service]}/{path.lstrip('/')}"
    body = await request.body()
    headers = {k: v for k, v in request.headers.items()
               if k.lower() not in ("host", "x-license-key", "content-length")}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.request(
                method=request.method, url=url,
                content=body, headers=headers,
                params=dict(request.query_params),
            )
    except httpx.TimeoutException as exc:
        raise HTTPException(504, "Upstream service timed out") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(502, "Upstream service unavailable") from exc
    try:
        return JSONResponse(content=resp.json(), status_code=resp.status_code)
    except Exception:
        return JSONResponse(content={"raw": resp.text}, status_code=resp.status_code)


# ── MONETIZATION routes (:8015) ───────────────────────────────────────────────

@app.post("/monetization/predict-promotion", tags=["Monetization"])
async def predict_promotion(request: Request, _: dict = Depends(get_license)):
    """
    پیش‌بینی بهترین پروموشن برای یه کاربر با XGBoost.

    Body:
    {
      "user_id": 123,
      "features": {"age": 0.4, "engagement": 0.7, "city_weight": 0.6, ...},
      "candidates": ["discount_10", "free_trial", "premium_badge"],
      "context": {}
    }

    Returns: variant (بهترین گزینه), score, all_scores
    """
    return await _proxy("monetization", "/api/predict-promotion", request)


@app.post("/monetization/feedback", tags=["Monetization"])
async def monetization_feedback(request: Request, _: dict = Depends(get_license)):
    """
    ارسال نتیجه واقعی (conversion=0/1) برای retrain خودکار.

    Body:
    {
      "user_id": 123,
      "variant": "discount_10",
      "features": {...},
      "label": 1
    }

    وقتی به MIN_RETRAIN_SAMPLES=100 برسه، مدل خودکار retrain می‌شه.
    """
    return await _proxy("monetization", "/api/feedback", request)


@app.post("/monetization/retrain", tags=["Monetization"])
async def monetization_retrain(request: Request, _: dict = Depends(get_license)):
    """Force retrain مدل بدون انتظار برای رسیدن به threshold"""
    return await _proxy("monetization", "/api/retrain", request)


# ── REVENUE routes (:8000) ────────────────────────────────────────────────────

@app.post("/revenue/predict/ltv", tags=["Revenue"])
async def predict_ltv(request: Request, _: dict = Depends(get_license)):
    """
    پیش‌بینی LTV (ارزش مادام‌العمر) یه کاربر با GradientBoosting.

    Body:
    {
      "userId": 123,
      "channelType": 0.5,          -- نوع کانال جذب (0-1)
      "keywordDifficulty": 0.5,    -- سختی کلمه کلیدی (0-1)
      "contentLength": 0.5,        -- طول محتوا (0-1)
      "timeToConversion": 30,      -- روزها تا تبدیل
      "cityWeight": 0.5,           -- وزن شهر (0-1)
      "intentScore": 0.5,          -- امتیاز قصد خرید (0-1)
      "engagementDepth": 5,        -- عمق تعامل
      "retentionImpact": 0.5,      -- تأثیر بازگشت (0-1)
      "campaignCost": 0,           -- هزینه کمپین
      "competitorPressure": 0.3,   -- فشار رقابتی (0-1)
      "seasonalityFactor": 1.0,    -- فاکتور فصلی
      "segmentSize": 0.5           -- اندازه سگمنت (0-1)
    }

    Returns: predicted_ltv, confidence_interval, feature_importance
    """
    return await _proxy("revenue", "/predict/ltv", request)


@app.post("/revenue/train", tags=["Revenue"])
async def train_revenue_model(request: Request, _: dict = Depends(get_license)):
    """
    Train/retrain مدل LTV با داده‌های labeled.
    Body: آرایه‌ای از LTVRequest با فیلد actualLtv پر شده.
    """
    return await _proxy("revenue", "/train", request)


# ── UPLIFT routes (:8031) ─────────────────────────────────────────────────────

@app.post("/uplift/train", tags=["Uplift"])
async def train_uplift(request: Request, _: dict = Depends(get_license)):
    """
    آموزش مدل Uplift — کمک می‌کنه بفهمیم کدوم کاربران واقعاً از کمپین تأثیر می‌گیرن.

    Body:
    {
      "data": [
        {"age": 25, "engagement": 0.7, "treatment": 1, "revenue": 150},
        ...
      ],
      "treatment_col": "treatment",
      "outcome_col": "revenue",
      "features": ["age", "engagement", ...]
    }

    اگه مدل کافی نباشه، fallback به avg_uplift می‌کنه (مدل نیازی به restart نداره).
    """
    return await _proxy("uplift", "/train", request)


@app.post("/uplift/predict", tags=["Uplift"])
async def predict_uplift(request: Request, _: dict = Depends(get_license)):
    """
    پیش‌بینی uplift برای دسته‌ای از کاربران.

    Body: {"features": [[0.4, 0.7, ...], [0.3, 0.5, ...], ...]}
    Returns: {"uplift": [0.12, 0.08, ...], "count": N}
    """
    return await _proxy("uplift", "/predict-uplift", request)


# ── FEEDBACK routes (:8004) ───────────────────────────────────────────────────

@app.post("/feedback/train", tags=["Feedback"])
async def feedback_train_incremental(request: Request, _: dict = Depends(get_license)):
    """
    Incremental training — بعد از هر تعامل کاربر (real-time).

    Body:
    {
      "userId": 123,
      "feature": "premium_cta",
      "phase": 2,
      "feedbackType": "click",
      "sentiment": "positive",
      "sentimentScore": 0.8,
      "impactScore": 0.6,
      "revenueImpact": 50.0,
      "value": {},
      "metadata": {}
    }
    """
    return await _proxy("feedback", "/feedback/train_incremental", request)


@app.post("/feedback/train/batch", tags=["Feedback"])
async def feedback_train_batch(request: Request, _: dict = Depends(get_license)):
    """
    Batch training — آموزش با تعداد زیادی رکورد تاریخی.
    Body: آرایه‌ای از FeedbackRequest.
    Returns: accuracy, phase, feature_importance
    """
    return await _proxy("feedback", "/feedback/train_batch", request)


@app.post("/feedback/predict", tags=["Feedback"])
async def feedback_predict(request: Request, _: dict = Depends(get_license)):
    """
    پیش‌بینی احتمال conversion یه کاربر بر اساس رفتارش.
    Body: یه FeedbackRequest
    Returns: conversion_probability, recommended_action
    """
    return await _proxy("feedback", "/feedback/predict", request)


@app.get("/feedback/metrics", tags=["Feedback"])
async def feedback_metrics(request: Request, _: dict = Depends(get_license)):
    """
    وضعیت مدل: feature importance، تعداد نمونه‌های آموزش، phase فعلی
    """
    return await _proxy("feedback", "/feedback/metrics", request)


# ── ADMIN ─────────────────────────────────────────────────────────────────────

@app.post("/admin/license/create", tags=["Admin"])
async def create_license(request: Request):
    if request.headers.get("X-Admin-Token") != ADMIN_TOKEN:
        raise HTTPException(403, "Admin token نامعتبر")
    import secrets
    body    = await request.json()
    raw_key = secrets.token_urlsafe(32)
    info    = {
        "domain":  body.get("domain", "*"),
        "plan":    body.get("plan", "basic"),
        "expires": body.get("expires", "2099-12-31"),
        "active":  True,
        "created": datetime.now().isoformat(),
    }
    await redis_client.set(f"{LICENSE_PREFIX}{_hash(raw_key)}", json.dumps(info))
    return {"license_key": raw_key, "key_hash": _hash(raw_key), **info}


@app.delete("/admin/license/{key_hash}", tags=["Admin"])
async def revoke_license(key_hash: str, request: Request):
    if request.headers.get("X-Admin-Token") != ADMIN_TOKEN:
        raise HTTPException(403, "Admin token نامعتبر")
    data = await redis_client.get(f"{LICENSE_PREFIX}{key_hash}")
    if not data:
        raise HTTPException(404, "License پیدا نشد")
    info = json.loads(data)
    info["active"] = False
    await redis_client.set(f"{LICENSE_PREFIX}{key_hash}", json.dumps(info))
    return {"status": "revoked"}


# ── HEALTH ────────────────────────────────────────────────────────────────────

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
    status = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in SERVICES.items():
            try:
                r = await client.get(f"{url}/health")
                body = r.json()
                status[name] = {
                    "status": "ok" if r.status_code == 200 else "degraded",
                    # اطلاعات مفید از هر سرویس
                    **{k: v for k, v in body.items()
                       if k in ("model_trained", "cv_score", "model_phase", "training_samples")},
                }
            except Exception as e:
                status[name] = {"status": "down", "error": str(e)}
    return {
        "status": "healthy" if all(item.get("status") == "ok" for item in status.values()) else ("degraded" if any(item.get("status") == "ok" for item in status.values()) else "unavailable"),
        "gateway":   "revenue_pack_v1",
        "timestamp": datetime.now().isoformat(),
        "services":  status,
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "name": "Revenue Pack Gateway",
        "version": "1.0.0",
        "services": {
            "monetization": {
                "url": SERVICES["monetization"],
                "endpoints": [
                    "POST /monetization/predict-promotion",
                    "POST /monetization/feedback",
                    "POST /monetization/retrain",
                ],
            },
            "revenue": {
                "url": SERVICES["revenue"],
                "endpoints": [
                    "POST /revenue/predict/ltv",
                    "POST /revenue/train",
                ],
            },
            "uplift": {
                "url": SERVICES["uplift"],
                "endpoints": [
                    "POST /uplift/train",
                    "POST /uplift/predict",
                ],
            },
            "feedback": {
                "url": SERVICES["feedback"],
                "endpoints": [
                    "POST /feedback/train",
                    "POST /feedback/train/batch",
                    "POST /feedback/predict",
                    "GET  /feedback/metrics",
                ],
            },
        },
    }
