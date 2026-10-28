# AI Packs — چهار پک هوش مصنوعی

چهار پک تخصصی AI با Gateway یکپارچه و افزونه‌های WordPress. وضعیت فعلی: نمونهٔ اولیهٔ یکپارچه‌سازی؛ پیش از فروش عمومی به تکمیل بسته‌بندی، تست کیفیت و hardening نیاز دارد.

- [ارزیابی فنی و تجاری](./docs/PRODUCT_AUDIT_2026-10-28.md)
- [نقشهٔ راه تجاری‌سازی](./docs/COMMERCIALIZATION_ROADMAP.md)

## پک‌ها

| پک | Gateway Port | سرویس‌ها | مدل‌ها |
|----|-------------|----------|--------|
| [SEO Pack](./seo-pack) | `:9000` | ai_seo, aeo_tracker, ai_backlink_quality, ai_seo_recommender | Prophet, CF, PageRank |
| [Safety Pack](./safety-pack) | `:9001` | ai_moderation, ai_verification, ai_image | DeepFace, NudeNet, SentenceTransformer |
| [Revenue Pack](./revenue-pack) | `:9002` | ai_monetization, ai_revenue, ai_uplift, ai_feedback | XGBoost, GBM, Uplift Tree |
| [Matching Pack](./matching-pack) | `:9003` | ml_service, embedded_ai, personality, ai_assistant, ai_support | MiniLM-L12, BERT فارسی |

## ساختار هر پک

```
{pack-name}/
├── gateway/
│   ├── main.py              ← FastAPI Gateway (License + Rate Limit + Proxy)
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.{pack}.yml
├── wordpress-plugin/
│   └── {pack}/
│       ├── {pack}.php       ← Main plugin file
│       ├── includes/
│       │   ├── class-api-client.php
│       │   └── class-license.php
│       └── admin/
│           ├── class-settings-page.php
│           └── class-demo-page.php  ← دمو زنده
└── README.md
```

## Deploy سریع

```bash
# ادغام با docker-compose اصلی
docker-compose \
  -f docker-compose.yml \
  -f ai-packs/seo-pack/docker-compose.seo-pack.yml \
  -f ai-packs/safety-pack/docker-compose.safety-pack.yml \
  -f ai-packs/revenue-pack/docker-compose.revenue-pack.yml \
  -f ai-packs/matching-pack/docker-compose.matching-pack.yml \
  up -d
```

## ساخت License Key

```bash
# SEO Pack
curl -X POST http://localhost:9000/admin/license/create \
  -H "X-Admin-Token: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain": "customer.com", "plan": "pro", "expires": "2027-01-01"}'
```

## Auth

هر request به Gateway:
```
X-License-Key: sk-xxxx...
```

## پلتفرم‌های پشتیبانی‌شده

- **WordPress** — پلاگین `.zip` آماده
- **Next.js / Node.js** — `X-License-Key` header در fetch
- **Laravel / PHP** — `Guzzle` با header
- **Android / iOS** — REST API مستقیم
- **Python** — `requests` با header
- هر پلتفرمی که REST API پشتیبانی کنه

## قیمت‌های فرضی برای تست بازار (نهایی نیستند)

| پک | قیمت فرضی |
|----|------|
| SEO Pack | $49/ماه |
| Safety Pack | $39/ماه |
| Revenue Pack | $59/ماه |
| Matching Pack | $69/ماه |
| همه پک‌ها | $179/ماه |


> **مهم:** قیمت‌های جدول بالا قیمت نهایی یا اثبات‌شده نیستند. پیش از انتشار عمومی باید با مشتریان هدف، هزینهٔ واقعی هر درخواست و کیفیت اندازه‌گیری‌شده اعتبارسنجی شوند. کلید API/License را فقط در backend نگه دارید؛ Gateway برای استفادهٔ مستقیم از مرورگر با کلید محرمانه طراحی نشده است.
