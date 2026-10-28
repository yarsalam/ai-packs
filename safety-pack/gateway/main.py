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

import os, hashlib, json, httpx
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
    return info


async def check_rate_limit(license_key: str):
    key = f"{RATE_LIMIT_PREFIX}{_hash(license_key)}"
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, 3600)
    if count > RATE_LIMIT_PER_HOUR:
        raise HTTPException(429, f"Rate limit: {RATE_LIMIT_PER_HOUR} req/hour")


async def get_license(request: Request) -> dict:
    key = request.headers.get("X-License-Key")
    info = await validate_license(key)
    await check_rate_limit(key)
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
    selfie_bytes  = await selfie.read()
    profile_bytes = await profile_photo.read()

    files = [
        ("selfie",        (selfie.filename,        selfie_bytes,  selfie.content_type)),
        ("profile_photo", (profile_photo.filename, profile_bytes, profile_photo.content_type)),
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
    file_bytes = await file.read()
    files = [("file", (file.filename, file_bytes, file.content_type))]
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
    file_bytes = await file.read()
    files = [("file", (file.filename, file_bytes, file.content_type))]
    return await _proxy_files("image", "/image/analyze", files)


@app.get("/image/status/{filename}", tags=["Image"])
async def image_status(filename: str, request: Request, _: dict = Depends(get_license)):
    """وضعیت پردازش پس‌زمینه یه تصویر"""
    return await _proxy_json("image", f"/image/status/{filename}", request)


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
                status[name] = "ok" if r.status_code == 200 else "degraded"
            except Exception:
                status[name] = "down"
    return {
        "status": "healthy" if all(value == "ok" for value in status.values()) else ("degraded" if any(value == "ok" for value in status.values()) else "unavailable"),
        "gateway":   "safety_pack_v1",
        "timestamp": datetime.now().isoformat(),
        "services":  status,
    }


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
