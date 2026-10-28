"""
Matching Pack Gateway
=====================
جلوی ۵ سرویس Matching می‌ایسته:
  - ml_service   :8000  → /match/*       (matching + recommendation + embedding cache)
  - embedded_ai  :8100  → /embed/*       (SentenceTransformer multilingual)
  - personality  :8100  → /personality/* (sentiment + emotion با مدل‌های محلی)
  - ai_assistant :8022  → /assistant/*   (analyze behavior + advice + chat)
  - ai_support   :8016  → /support/*     (ticket analysis + BERT فارسی)

وابستگی‌های مهم:
  - ml_service داخلاً به embedded_ai:8100 وصله (EmbeddingClient)
  - personality مدل‌های /models/sentiment و /models/emotion روی volume می‌خواد
  - ai_support مدل BERT فارسی روی /app/models می‌خواد
  - ai_assistant به Redis برای cache وصله
  - embedded_ai به Redis برای cache embedding وصله
"""

import os, hashlib, json, httpx
from datetime import datetime, date, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import redis.asyncio as aioredis

# ── Config ────────────────────────────────────────────────────────────────────
SERVICES = {
    "match":       os.getenv("ML_SERVICE_URL",    "http://ml_service:8000"),
    "embed":       os.getenv("EMBEDDED_AI_URL",   "http://embedded_ai:8100"),
    "personality": os.getenv("PERSONALITY_URL",   "http://personality:8100"),
    "assistant":   os.getenv("AI_ASSISTANT_URL",  "http://ai_assistant:8022"),
    "support":     os.getenv("AI_SUPPORT_URL",    "http://ai_support:8016"),
}

REDIS_URL           = os.getenv("REDIS_URL",   "redis://redis:6379/0")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
LICENSE_PREFIX      = "matching_license:"
RATE_LIMIT_PREFIX   = "matching_ratelimit:"
RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "3000"))

# Billable usage credits are provisional defaults; adjust after measuring inference cost.
PLAN_LIMITS = {
    "free": {"hourly_units": 60, "monthly_units": 1000},
    "basic": {"hourly_units": min(200, RATE_LIMIT_PER_HOUR), "monthly_units": 5000},
    "pro": {"hourly_units": RATE_LIMIT_PER_HOUR, "monthly_units": 50000},
    "enterprise": {"hourly_units": RATE_LIMIT_PER_HOUR * 5, "monthly_units": 250000},
}
USAGE_PREFIX = "matching_usage:"
TRAINING_PATHS = {
    "/recommend/train", "/monetization/retrain", "/revenue/train",
    "/uplift/train", "/feedback/train", "/feedback/train/batch",
}

app = FastAPI(
    title="Matching Pack Gateway",
    version="1.0.0",
    description="Unified gateway for ml_service, embedded_ai, personality, ai_assistant, ai_support",
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


# ── Generic proxy ─────────────────────────────────────────────────────────────
async def _proxy(service: str, path: str, request: Request) -> JSONResponse:
    url  = f"{SERVICES[service]}/{path.lstrip('/')}"
    body = await request.body()
    headers = {k: v for k, v in request.headers.items()
               if k.lower() not in ("host", "x-license-key", "content-length")}
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:  # 60s — مدل‌های NLP کند هستن
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


# ── ML SERVICE routes (:8000) ─────────────────────────────────────────────────

@app.post("/match/embed", tags=["Matching"])
async def match_embed(request: Request, _: dict = Depends(get_license)):
    """
    Embed یه متن و cache کردن embedding روی Redis با key کاربر.

    Body: {"text": "توضیح درباره کاربر...", "user_id": 123}
    Returns: embedding (384-dim), model, version
    """
    return await _proxy("match", "/api/embed", request)


@app.post("/match/recommend", tags=["Matching"])
async def match_recommend(request: Request, _: dict = Depends(get_license)):
    """
    پیشنهاد بهترین کاربران از لیست کاندیداها برای یه کاربر.

    Body:
    {
      "user_id": 123,
      "candidates": [456, 789, 101, 202],
      "limit": 10
    }

    embedding کاربر باید از قبل در Redis باشه (اول /match/embed بزن).
    Returns: ranked list از کاندیداها با similarity score
    """
    return await _proxy("match", "/api/recommend", request)


@app.post("/match/predict", tags=["Matching"])
async def match_predict(request: Request, _: dict = Depends(get_license)):
    """
    Match score بین دو کاربر.

    Body: {"user_a": 123, "user_b": 456}
    Returns: {"score": 0.87, "user_a": 123, "user_b": 456}
    """
    return await _proxy("match", "/api/predict", request)


@app.post("/match/track-events", tags=["Matching"])
async def match_track_events(request: Request, _: dict = Depends(get_license)):
    """
    Track رویدادهای کاربر (like, skip, message) برای بهبود مدل.

    Body: {"user_id": 123, "events": [{"type": "like", "target": 456}, ...]}
    """
    return await _proxy("match", "/api/internal/track-events", request)


# ── EMBEDDED AI routes (:8100) ────────────────────────────────────────────────

@app.post("/embed/text", tags=["Embedding"])
async def embed_text(request: Request, _: dict = Depends(get_license)):
    """
    تبدیل یه متن به embedding vector.
    مدل: paraphrase-multilingual-MiniLM-L12-v2 (فارسی + انگلیسی)

    Body: {"text": "متن شما"}
    Returns: {"embedding": [...384 float...], "model_name": "...", "dimension": 384}
    """
    return await _proxy("embed", "/embed", request)


@app.post("/embed/batch", tags=["Embedding"])
async def embed_batch(request: Request, _: dict = Depends(get_license)):
    """
    Embed دسته‌ای چند متن.

    Body: {"texts": ["متن اول", "متن دوم", ...]}
    """
    return await _proxy("embed", "/embed/batch", request)


@app.post("/embed/similarity", tags=["Embedding"])
async def embed_similarity(request: Request, _: dict = Depends(get_license)):
    """
    Cosine similarity بین دو vector.

    Body: {"vector_a": [...], "vector_b": [...]}
    Returns: {"similarity": 0.87}
    """
    return await _proxy("embed", "/similarity", request)


# ── PERSONALITY routes (:8100) ────────────────────────────────────────────────

@app.post("/personality/sentiment", tags=["Personality"])
async def personality_sentiment(request: Request, _: dict = Depends(get_license)):
    """
    تحلیل sentiment چند پیام.
    مدل محلی روی /models/sentiment (Transformers pipeline)

    Body: {"messages": ["خیلی خوشحالم!", "امروز بد بود"]}
    Returns: {"sentiments": [{"label": "positive", "score": 0.98}, ...]}

    ⚠️ اولین call کند است — مدل lazy-load می‌شود.
    """
    return await _proxy("personality", "/analyze_sentiment", request)


@app.post("/personality/emotion", tags=["Personality"])
async def personality_emotion(request: Request, _: dict = Depends(get_license)):
    """
    تشخیص emotion چند پیام.
    مدل محلی روی /models/emotion

    Body: {"messages": ["دلم برات تنگ شده", "خیلی عصبانیم"]}
    Returns: {"emotions": [{"label": "love", "score": 0.92}, ...]}
    """
    return await _proxy("personality", "/analyze_emotion", request)


# ── AI ASSISTANT routes (:8022) ───────────────────────────────────────────────

@app.post("/assistant/analyze", tags=["Assistant"])
async def assistant_analyze(request: Request, _: dict = Depends(get_license)):
    """
    آنالیز کامل یه کاربر: personality + behavior + sentiment.
    نتیجه در Redis cache می‌شه (7 روز).

    Body:
    {
      "user_id": 123,
      "bio": "علاقه‌مند به کوهنوردی و موسیقی...",
      "messages": ["سلام خوش اومدی", "چه سرگرمی‌هایی داری؟"],
      "events": [
        {"type": "like", "target_id": 456, "timestamp": "2025-01-01T10:00:00"},
        {"type": "skip", "target_id": 789, "timestamp": "2025-01-01T10:01:00"}
      ]
    }

    Returns: personality (traits), behavior (rates), sentiment
    """
    return await _proxy("assistant", "/api/assistant/analyze", request)


@app.get("/assistant/advice/{user_id}", tags=["Assistant"])
async def assistant_advice(user_id: int, request: Request, _: dict = Depends(get_license)):
    """
    پیشنهادات شخصی‌سازی‌شده برای بهبود پروفایل و match rate.
    ابتدا /assistant/analyze باید صدا زده شده باشه.

    Returns: tips (لیست توصیه‌ها)، personality_summary، action_items
    """
    return await _proxy("assistant", f"/api/assistant/advice/{user_id}", request)


@app.post("/assistant/chat", tags=["Assistant"])
async def assistant_chat(request: Request, _: dict = Depends(get_license)):
    """
    چت با دستیار هوشمند — راهنمایی در استفاده از اپ.

    Body: {"user_id": 123, "message": "چطور پروفایلم رو بهتر کنم؟"}
    """
    return await _proxy("assistant", "/api/assistant/chat", request)


# ── AI SUPPORT routes (:8016) ─────────────────────────────────────────────────

@app.post("/support/analyze", tags=["Support"])
async def support_analyze(request: Request, _: dict = Depends(get_license)):
    """
    آنالیز تیکت پشتیبانی با BERT فارسی.

    Body:
    {
      "ticketId": 1001,
      "content": "نمیتونم وارد حسابم بشم. رمزم رو فراموش کردم.",
      "userId": 123,
      "userTier": "premium",
      "totalPurchases": 5
    }

    Returns:
      category (technical/billing/account/feature_request/report),
      priority (urgent/high/medium/low),
      suggested_response (پیام پیشنهادی),
      estimated_resolution_hours,
      revenue_impact_score
    """
    return await _proxy("support", "/api/analyze", request)


@app.get("/support/tickets/{ticket_id}/analysis", tags=["Support"])
async def support_get_analysis(ticket_id: int, request: Request, _: dict = Depends(get_license)):
    """تحلیل cache شده یه تیکت (بعد از POST /support/analyze)"""
    return await _proxy("support", f"/api/tickets/{ticket_id}/analysis", request)


@app.post("/support/feedback", tags=["Support"])
async def support_feedback(request: Request, _: dict = Depends(get_license)):
    """
    فیدبک بعد از حل تیکت — مدل از آن یاد می‌گیرد.

    Body:
    {
      "ticketId": 1001,
      "rating": 5,
      "comment": "مشکل حل شد",
      "resolutionTime": 30
    }
    """
    return await _proxy("support", "/api/feedback", request)


@app.get("/support/seo-insights", tags=["Support"])
async def support_seo_insights(request: Request, _: dict = Depends(get_license)):
    """
    تحلیل محتوای تیکت‌ها برای بهبود SEO.
    کلمات پرتکرار در مشکلات کاربران → keyword opportunity
    """
    return await _proxy("support", "/api/seo-insights", request)


# ── ADMIN ─────────────────────────────────────────────────────────────────────

@app.post("/admin/license/create", tags=["Admin"])
async def create_license(request: Request):
    admin_token = request.headers.get("X-Admin-Token")
    if not admin_token or not secrets.compare_digest(admin_token, ADMIN_TOKEN):
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
    admin_token = request.headers.get("X-Admin-Token")
    if not admin_token or not secrets.compare_digest(admin_token, ADMIN_TOKEN):
        raise HTTPException(403, "Admin token نامعتبر")
    data = await redis_client.get(f"{LICENSE_PREFIX}{key_hash}")
    if not data:
        raise HTTPException(404, "License پیدا نشد")
    info = json.loads(data)
    info["active"] = False
    await redis_client.set(f"{LICENSE_PREFIX}{key_hash}", json.dumps(info))
    return {"status": "revoked"}


# ── HEALTH ────────────────────────────────────────────────────────────────────

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
    status = {}
    async with httpx.AsyncClient(timeout=8.0) as client:
        for name, url in SERVICES.items():
            try:
                r = await client.get(f"{url}/health")
                body = r.json()
                status[name] = {
                    "status": "ok" if r.status_code == 200 else "degraded",
                    **{k: v for k, v in body.items()
                       if k in ("model_loaded", "models_loaded", "redis", "cache_size")},
                }
            except Exception as e:
                status[name] = {"status": "down", "error": str(e)}
    payload = {
        "status": "healthy" if all(item.get("status") == "ok" for item in status.values()) else ("degraded" if any(item.get("status") == "ok" for item in status.values()) else "unavailable"),
        "gateway":   "matching_pack_v1",
        "timestamp": datetime.now().isoformat(),
        "services":  status,
        "note": "personality سرویس اولین بار slow-start دارد (lazy model load)",
    }
    return JSONResponse(content=payload, status_code=503 if payload["status"] == "unavailable" else 200)




@app.get("/", tags=["System"])
async def root():
    return {
        "name": "Matching Pack Gateway",
        "version": "1.0.0",
        "services": {
            "match":       ["POST /match/embed", "POST /match/recommend", "POST /match/predict", "POST /match/track-events"],
            "embed":       ["POST /embed/text", "POST /embed/batch", "POST /embed/similarity"],
            "personality": ["POST /personality/sentiment", "POST /personality/emotion"],
            "assistant":   ["POST /assistant/analyze", "GET /assistant/advice/{user_id}", "POST /assistant/chat"],
            "support":     ["POST /support/analyze", "GET /support/tickets/{id}/analysis", "POST /support/feedback", "GET /support/seo-insights"],
        },
        "dependencies": {
            "ml_service":  "embedded_ai:8100 (EmbeddingClient داخلی)",
            "personality": "/models/sentiment و /models/emotion (volume)",
            "ai_support":  "/app/models (BERT فارسی، volume)",
            "ai_assistant": "Redis (cache کاربران)",
            "embedded_ai": "Redis (cache embedding)",
        },
    }
