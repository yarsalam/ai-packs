"""
Safety Pack Gateway
===================
جلوی ۳ سرویس Safety می‌ایسته:
  - ai_moderation   :8018  → /moderate/*
  - ai_verification :8017  → /verify/*
  - ai_image        :8102  → /image/*

نکات مهم این Gateway نسبت به SEO Pack:
  1. ai_verification و ai_image فایل multipart می‌گیرن — باید stream بشن نه buffer
  2. ai_moderation به embedded_ai:8100 وابسته‌ست (semantic check)
  3. ai_image یه pipeline داره: EXIF clean → NSFW check → analyze
"""

import os, hashlib, json, httpx, secrets
from datetime import datetime, date, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
import redis.asyncio as aioredis

# ── Config ──────────────────────────────────────────────────────────────────
SERVICES = {
    "moderation":   os.getenv("AI_MODERATION_URL",   "http://ai_moderation:8018"),
    "verification": os.getenv("AI_VERIFICATION_URL", "http://ai_verification:8017"),
    "image":        os.getenv("AI_IMAGE_URL",         "http://ai_image:8100"),
}

REDIS_URL            = os.getenv("REDIS_URL",   "redis://redis:6379/0")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
LICENSE_PREFIX       = "safety_license:"
RATE_LIMIT_PREFIX    = "safety_ratelimit:"
RATE_LIMIT_PER_HOUR  = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))

# Billable usage credits are provisional defaults; adjust after measuring inference cost.
PLAN_LIMITS = {
    "free": {"hourly_units": 60, "monthly_units": 1000},
    "basic": {"hourly_units": min(200, RATE_LIMIT_PER_HOUR), "monthly_units": 5000},
    "pro": {"hourly_units": RATE_LIMIT_PER_HOUR, "monthly_units": 50000},
    "enterprise": {"hourly_units": RATE_LIMIT_PER_HOUR * 5, "monthly_units": 250000},
}
USAGE_PREFIX = "safety_usage:"
TRAINING_PATHS = {
    "/recommend/train", "/monetization/retrain", "/revenue/train",
    "/uplift/train", "/feedback/train", "/feedback/train/batch",
}

app = FastAPI(
    title="Safety Pack Gateway",
    version="1.0.0",
    description="Unified gateway for ai_moderation, ai_verification, ai_image",
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


# ── License ──────────────────────────────────────────────────────────────────
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


async def validate_license(license_key: str) -> dict:
    if not license_key:
        raise HTTPException(401, "License key الزامی است")
    data = await redis_client.get(f"{LICENSE_PREFIX}{_hash(license_key)}")
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
    # Polling an async image job is cheap; running image/face inference is expensive.
    if path.startswith("/image/status/"):
        return 1
    if path == "/verify/face" or path in {"/image/upload", "/image/analyze"}:
        return 10
    if path.endswith("/batch"):
        return 5
    if (
        path.startswith("/moderate/")
        or path.startswith("/personality/")
        or path.startswith("/assistant/")
        or path.startswith("/match/")
        or path.startswith("/support/")
        or path.startswith("/embed/")
        or path.startswith("/seo/")
        or path.startswith("/aeo/")
        or path.startswith("/backlink/")
        or path.startswith("/recommend/")
    ):
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


# ── JSON Proxy (moderation) ───────────────────────────────────────────────────
async def _proxy_json(service: str, path: str, request: Request) -> JSONResponse:
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


async def _read_bounded_image(file: UploadFile) -> tuple[str, bytes, str]:
    """Bound per-file memory before forwarding image data to the model service."""
    if not file.content_type or not file.content_type.lower().startswith("image/"):
        raise HTTPException(415, "Uploaded file must have an image content type")
    contents = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"Each image must be <= {MAX_UPLOAD_BYTES} bytes")
    if not contents:
        raise HTTPException(400, "Uploaded image is empty")
    return (file.filename or "upload.jpg", contents, file.content_type)


# ── File Proxy (verification, image) — streams multipart ────────────────────
async def _proxy_files(service: str, path: str, files: list, data: dict = None) -> JSONResponse:
    """
    files: list of ("field_name", (filename, bytes, content_type))
    data:  dict of extra form fields
    """
    url = f"{SERVICES[service]}/{path.lstrip('/')}"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, files=files, data=data or {})
    except httpx.TimeoutException as exc:
        raise HTTPException(504, "Upstream service timed out") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(502, "Upstream service unavailable") from exc
    try:
        return JSONResponse(content=resp.json(), status_code=resp.status_code)
    except Exception:
        return JSONResponse(content={"raw": resp.text}, status_code=resp.status_code)


# ── MODERATION Routes ─────────────────────────────────────────────────────────

@app.post("/moderate/text", tags=["Moderation"])
async def moderate_text(request: Request, _: dict = Depends(get_license)):
    """
    بررسی یه متن.
    Body: {"text": "...", "context": "message|bio|comment", "user_id": 123}
    
    سرویس دو لایه داره:
      1. Rule-based (کلمات ممنوع، لینک‌های خارجی)
      2. Semantic (embedding similarity با نمونه‌های مشکل‌دار)
    """
    return await _proxy_json("moderation", "/moderate", request)


@app.post("/moderate/batch", tags=["Moderation"])
async def moderate_batch(request: Request, _: dict = Depends(get_license)):
    """
    بررسی دسته‌ای چند متن.
    Body: {"texts": ["...", "..."], "context": "message"}
    Returns: total, blocked, allowed + جزئیات هر متن
    """
    return await _proxy_json("moderation", "/moderate/batch", request)


# ── VERIFICATION Routes ───────────────────────────────────────────────────────

@app.post("/verify/face", tags=["Verification"])
async def verify_face(
    selfie:        UploadFile = File(..., description="سلفی کاربر"),
    profile_photo: UploadFile = File(..., description="عکس پروفایل"),
    _: dict = Depends(get_license),
):
    """
    تطابق چهره سلفی با عکس پروفایل — با DeepFace/Facenet.
    Returns: verified (bool), confidence (0-1), distance, message
    
    حداکثر حجم: 10MB هر فایل
    """
    selfie_file = await _read_bounded_image(selfie)
    profile_file = await _read_bounded_image(profile_photo)

    files = [
        ("selfie", selfie_file),
        ("profile_photo", profile_file),
    ]
    return await _proxy_files("verification", "/verify", files)


# ── IMAGE Routes ──────────────────────────────────────────────────────────────

@app.post("/image/upload", tags=["Image"])
async def image_upload(
    file: UploadFile = File(..., description="تصویر برای آپلود"),
    _: dict = Depends(get_license),
):
    """
    Pipeline کامل آپلود تصویر:
      1. EXIF clean (حذف متادیتا برای حریم خصوصی)
      2. NSFW detection (با NudeNet)
      3. پردازش پس‌زمینه (تحلیل چهره + کیفیت)
    
    اگه NSFW باشه: 400 + reason
    اگه OK باشه: 200 + status: accepted
    """
    image_file = await _read_bounded_image(file)
    files = [("file", image_file)]
    return await _proxy_files("image", "/image/upload", files)


@app.post("/image/analyze", tags=["Image"])
async def image_analyze(
    file: UploadFile = File(...),
    _: dict = Depends(get_license),
):
    """
    تحلیل کامل تصویر: quality score + face detection
    Returns: quality_score, faces (list)
    """
    image_file = await _read_bounded_image(file)
    files = [("file", image_file)]
    return await _proxy_files("image", "/image/analyze", files)


@app.get("/image/status/{filename}", tags=["Image"])
async def image_status(filename: str, request: Request, _: dict = Depends(get_license)):
    """وضعیت پردازش پس‌زمینه یه تصویر"""
    return await _proxy_json("image", f"/image/status/{filename}", request)


# ── ADMIN ─────────────────────────────────────────────────────────────────────

@app.post("/admin/license/create", tags=["Admin"])
async def create_license(request: Request):
    admin_token = request.headers.get("X-Admin-Token")
    if not admin_token or not secrets.compare_digest(admin_token, ADMIN_TOKEN):
        raise HTTPException(403, "Admin token نامعتبر")

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
    info    = {
        "domain":  body.get("domain", "*"),
        "plan":    plan,
        "expires": expires,
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
                status[name] = "ok" if healthy else "degraded"
            except Exception:
                status[name] = "down"
    payload = {
        "status": "healthy" if all(value == "ok" for value in status.values()) else ("degraded" if any(value == "ok" for value in status.values()) else "unavailable"),
        "gateway":   "safety_pack_v1",
        "timestamp": datetime.now().isoformat(),
        "services":  status,
    }
    return JSONResponse(content=payload, status_code=503 if payload["status"] == "unavailable" else 200)




@app.get("/", tags=["System"])
async def root():
    return {
        "name": "Safety Pack Gateway",
        "version": "1.0.0",
        "endpoints": {
            "moderation":   ["POST /moderate/text", "POST /moderate/batch"],
            "verification": ["POST /verify/face"],
            "image":        ["POST /image/upload", "POST /image/analyze", "GET /image/status/{filename}"],
        },
        "note": "ai_moderation نیاز به embedded_ai:8100 دارد (semantic similarity)",
    }
