# Revenue Pack — راهنمای Deploy

## ساختار

```
revenue-pack/
├── gateway/
│   ├── main.py                          ← FastAPI Gateway
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.revenue-pack.yml
└── wordpress-plugin/
    └── revenue-pack/
        ├── revenue-pack.php
        ├── includes/
        │   ├── class-api-client.php     ← همه API calls
        │   └── class-license.php
        └── admin/
            ├── class-settings-page.php
            └── class-demo-page.php      ← دمو زنده ۴ سرویس
```

## پورت‌های واقعی (از docker-compose.yml اصلی)

| سرویس | Host Port | Container Port | مدل |
|-------|-----------|----------------|-----|
| ai_monetization | :8015 | :8015 | XGBoost |
| ai_revenue | :8006 | :8000 | GradientBoosting |
| ai_uplift | :8031 | :8031 | Uplift Tree |
| ai_feedback | :8005 | :8004 | GBM + RandomForest |
| **revenue_pack_gateway** | **:9002** | :8000 | — |

## نکته‌های مهم

### ai_monetization
- به Redis وابسته برای buffer کردن feedback
- وقتی ۱۰۰ نمونه feedback جمع بشه، مدل خودکار retrain می‌شه
- مدل XGBoost روی volume ذخیره می‌شه

### ai_revenue
- مدل GBM روی `/app/models` ذخیره می‌شه (volume لازمه)
- اگه مدل train نشده باشه، endpoint `/predict/ltv` خطا می‌ده — اول باید `/train` بزنی

### ai_uplift
- **Fallback mode**: اگه مدل train نشده، avg_uplift برمی‌گردونه — crash نمی‌کنه
- هر دو مدل و meta روی volume ذخیره می‌شن

### ai_feedback
- دو حالت training: incremental (real-time) و batch (تاریخی)
- Phase 1→2→3 با رسیدن به threshold های نمونه
- Feature importance بعد از هر train به‌روز می‌شه

## Deploy

```bash
docker-compose -f docker-compose.yml \
               -f docker-compose.revenue-pack.yml up -d revenue_pack_gateway
```

## ساخت License Key

```bash
curl -X POST http://localhost:9002/admin/license/create \
  -H "X-Admin-Token: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain": "customer.com", "plan": "pro", "expires": "2027-01-01"}'
```

## Endpoints

| Endpoint | سرویس | مدل | عملکرد |
|----------|-------|-----|--------|
| `POST /monetization/predict-promotion` | ai_monetization | XGBoost | بهترین پروموشن |
| `POST /monetization/feedback` | ai_monetization | — | ثبت نتیجه واقعی |
| `POST /monetization/retrain` | ai_monetization | XGBoost | Force retrain |
| `POST /revenue/predict/ltv` | ai_revenue | GBM | پیش‌بینی LTV |
| `POST /revenue/train` | ai_revenue | GBM | آموزش مدل |
| `POST /uplift/train` | ai_uplift | Uplift | آموزش مدل |
| `POST /uplift/predict` | ai_uplift | Uplift | پیش‌بینی uplift |
| `POST /feedback/train` | ai_feedback | GBM+RF | Incremental train |
| `POST /feedback/train/batch` | ai_feedback | GBM+RF | Batch train |
| `POST /feedback/predict` | ai_feedback | GBM+RF | احتمال conversion |
| `GET  /feedback/metrics` | ai_feedback | — | آمار مدل |
| `GET  /health` | gateway | — | وضعیت همه |

## مقایسه با پک‌های قبلی

| | SEO Pack | Safety Pack | Revenue Pack |
|-|----------|-------------|--------------|
| Port gateway | :9000 | :9001 | :9002 |
| نوع داده | JSON | JSON + File | JSON |
| وابستگی | — | embedded_ai | Redis (monetization) |
| Volume | — | — | ✅ (4 سرویس) |
| Auto-retrain | — | — | ✅ (monetization) |
| Fallback | — | — | ✅ (uplift) |
