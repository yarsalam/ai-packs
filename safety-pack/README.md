> **یادداشت بسته‌بندی:** این راهنما و فایل Compose کنار آن برای توسعهٔ داخلی است و به checkout سرویس‌های اصلی mobApp وابستگی دارد. برای مشتری، ZIP مستقل ساخته‌شده با `scripts/build_distributions.py` و workflow توزیع را ارائه کنید؛ این پوشه را مستقیماً به‌عنوان نصب مستقل نفروشید.

# Safety Pack — راهنمای Deploy

## ساختار

```
safety-pack/
├── gateway/
│   ├── main.py              ← FastAPI Gateway (License + Proxy + File streaming)
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.safety-pack.yml
└── wordpress-plugin/
    └── safety-pack/
        ├── safety-pack.php
        ├── includes/
        │   ├── class-api-client.php   ← JSON + multipart cURL
        │   ├── class-license.php
        │   └── class-hooks.php        ← Auto-moderate + NSFW block
        └── admin/
            ├── class-settings-page.php
            └── class-demo-page.php    ← دمو زنده با فایل آپلود واقعی
```

## تفاوت با SEO Pack

| موضوع | SEO Pack | Safety Pack |
|-------|----------|-------------|
| نوع درخواست | JSON | JSON + **multipart file** |
| وابستگی مخفی | ندارد | `ai_moderation` → `embedded_ai:8100` |
| Hook خودکار | ندارد | **فیلتر کامنت + بلاک آپلود NSFW** |
| REST API | ندارد | `POST /wp-json/safety-pack/v1/moderate` |

## پورت‌های سرویس‌ها

| سرویس | پورت | وابستگی |
|-------|------|---------|
| ai_moderation | :8018 | Redis + embedded_ai:8100 |
| ai_verification | :8017 | — |
| ai_image | :8102 (host) / 8100 (container) | Redis |
| **safety_pack_gateway** | :9001 | همه بالا |

## Deploy

```bash
docker-compose -f docker-compose.yml \
               -f docker-compose.safety-pack.yml up -d safety_pack_gateway
```

## ساخت License Key

```bash
curl -X POST http://localhost:9001/admin/license/create \
  -H "X-Admin-Token: YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain": "customer.com", "plan": "pro", "expires": "2027-01-01"}'
```

## Endpoints فعال

| Endpoint | عملکرد |
|----------|--------|
| `POST /moderate/text` | بررسی یه متن |
| `POST /moderate/batch` | بررسی دسته‌ای |
| `POST /verify/face` | تطابق چهره (multipart) |
| `POST /image/upload` | آپلود + NSFW check (multipart) |
| `POST /image/analyze` | تحلیل کامل تصویر (multipart) |
| `GET  /image/status/{filename}` | وضعیت پردازش |
| `GET  /health` | وضعیت همه سرویس‌ها |

## قابلیت‌های خودکار WordPress

بعد از نصب پلاگین و فعال کردن در تنظیمات:

**فیلتر کامنت** — هر کامنت قبل از ثبت بررسی می‌شه. اگه حاوی لینک خارجی، آیدی تلگرام، یا محتوای خشونت‌آمیز باشه، مسدود می‌شه.

**NSFW Block** — هر تصویر قبل از آپلود در مدیا بررسی می‌شه. اگه محتوای نامناسب داشته باشه رد می‌شه.

**REST API** — توسعه‌دهندگان می‌تونن از `POST /wp-json/safety-pack/v1/moderate` برای بررسی متن از frontend استفاده کنن.
