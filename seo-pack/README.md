> **یادداشت بسته‌بندی:** این راهنما و فایل Compose کنار آن برای توسعهٔ داخلی است و به checkout سرویس‌های اصلی mobApp وابستگی دارد. برای مشتری، ZIP مستقل ساخته‌شده با `scripts/build_distributions.py` و workflow توزیع را ارائه کنید؛ این پوشه را مستقیماً به‌عنوان نصب مستقل نفروشید.

# SEO Pack — راهنمای Deploy

## ساختار فایل‌ها

```
seo-pack/
├── gateway/
│   ├── main.py              ← FastAPI Gateway (License + Proxy)
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.seo-pack.yml
└── wordpress-plugin/
    └── seo-pack/
        ├── seo-pack.php                         ← Main plugin file
        ├── includes/
        │   ├── class-api-client.php             ← همه API calls
        │   └── class-license.php                ← License validation
        └── admin/
            ├── class-settings-page.php          ← پنل تنظیمات
            └── class-demo-page.php              ← دمو زنده ۴ سرویس
```

## مراحل Deploy

### ۱. Gateway رو اضافه کن

```bash
# توی پوشه اصلی پروژه
docker-compose -f docker-compose.yml \
               -f docker-compose.seo-pack.yml up -d seo_pack_gateway
```

### ۲. یه License Key بساز

```bash
curl -X POST http://localhost:9000/admin/license/create \
  -H "X-Admin-Token: YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain": "customer-site.com", "plan": "pro", "expires": "2026-12-31"}'
```

جواب:
```json
{
  "license_key": "sk-abcdef...",   ← این رو به مشتری بده
  "key_hash": "sha256...",
  "domain": "customer-site.com",
  "plan": "pro",
  "expires": "2026-12-31",
  "active": true
}
```

### ۳. Nginx برای Gateway

```nginx
location /seo-pack/ {
    proxy_pass http://127.0.0.1:9000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

### ۴. پلاگین WordPress نصب کن

```bash
# پوشه seo-pack رو zip کن
cd wordpress-plugin && zip -r seo-pack.zip seo-pack/
```

- آپلود از طریق **افزونه‌ها > افزودن > آپلود**
- License key وارد کن در **SEO Pack AI > تنظیمات**
- از **SEO Pack AI > دمو زنده** هر سرویس رو تست کن

## Endpoints فعال بعد از Gateway

| Endpoint | سرویس پشتی | عملکرد |
|----------|------------|--------|
| `POST /seo/predict/traffic` | ai_seo :8021 | پیش‌بینی ترافیک |
| `POST /seo/audit/url` | ai_seo :8021 | چک‌لیست فنی HTML برای URL عمومی (غیر از امتیاز رتبه‌بندی گوگل) |
| `POST /seo/feedback/campaign` | ai_seo :8021 | فیدبک کمپین |
| `POST /aeo/check-mentions` | aeo_tracker :8030 | چک AEO |
| `GET  /aeo/history/{brand}` | aeo_tracker :8030 | تاریخچه AEO |
| `POST /backlink/trust-flow` | ai_backlink :8032 | Trust Flow |
| `POST /backlink/topic-similarity` | ai_backlink :8032 | شباهت موضوعی |
| `POST /recommend/recommend` | ai_recommender :8033 | پیشنهادات |
| `POST /recommend/train` | ai_recommender :8033 | آموزش مدل |
| `GET  /health` | gateway | وضعیت همه سرویس‌ها |

## AEO چندموتوره (OpenAI + Perplexity)

در `docker-compose.seo-pack.yml` دو متغیر مستقل برای AEO وجود دارد:
- `OPENAI_API_KEY`
- `PERPLEXITY_API_KEY` (اختیاری؛ مدل پیش‌فرض `sonar` با `PERPLEXITY_MODEL` قابل تغییر است)

حداقل یکی از دو کلید را تنظیم کنید. اگر هر دو تنظیم شوند، درخواست پیش‌فرض هر دو engine را اجرا می‌کند و خروجی هر engine را جدا نگه می‌دارد؛ نرخ mention بین engineها با هم میانگین‌گیری نمی‌شود. برای انتخاب صریح:

```json
{
  "brand": "Example Brand",
  "prompts": ["Which tools are useful for ...?"],
  "engines": ["openai", "perplexity"]
}
```

پاسخ شامل `mention_rate_by_engine` و نتایج جداگانه است. Citationهای Perplexity در `results[].citations` ثبت می‌شوند. اگر کلید یک engine تنظیم نشده باشد، آن engine با وضعیت `unavailable` گزارش می‌شود و هرگز به‌عنوان «عدم mention» محاسبه نمی‌شود. برای چند engine، فیلد کلی `mention_rate` برابر null است تا عدد گمراه‌کننده ساخته نشود.

## Auth

هر request باید داشته باشه:
```
X-License-Key: sk-xxxx...
```
کلید را فقط در header بفرستید؛ قرار دادن آن در URL پشتیبانی نمی‌شود.

## Rate Limit

پیش‌فرض: ۵۰۰ درخواست در ساعت per license key
تغییر: `RATE_LIMIT_PER_HOUR` env در docker-compose
