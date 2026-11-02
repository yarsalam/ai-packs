> **یادداشت بسته‌بندی:** این راهنما و فایل Compose کنار آن برای توسعهٔ داخلی است و به checkout سرویس‌های اصلی mobApp وابستگی دارد. برای مشتری، ZIP مستقل ساخته‌شده با `scripts/build_distributions.py` و workflow توزیع را ارائه کنید؛ این پوشه را مستقیماً به‌عنوان نصب مستقل نفروشید.

# Matching Pack — راهنمای Deploy

## ساختار

```
matching-pack/
├── gateway/
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.matching-pack.yml
└── wordpress-plugin/
    └── matching-pack/
        ├── matching-pack.php
        ├── includes/
        │   ├── class-api-client.php    ← همه API calls (timeout=60s برای NLP)
        │   └── class-license.php
        └── admin/
            ├── class-settings-page.php
            └── class-demo-page.php     ← دمو زنده ۵ سرویس با ۵ tab
```

## پورت‌های واقعی (از docker-compose.yml اصلی)

| سرویس | Host Port | Container Port | مدل | حافظه |
|-------|-----------|----------------|-----|-------|
| ml_service | :8007 | :8000 | Cosine Similarity | ~512MB |
| embedded_ai | :8104 | :8100 | MiniLM-L12-v2 | ~2GB |
| personality | :8101 | :8100 | HuggingFace local | ~4GB |
| ai_assistant | :8022 | :8022 | Rule + NLP | ~256MB |
| ai_support | :8016 | :8016 | BERT فارسی | ~3GB |
| **matching_pack_gateway** | **:9003** | :8000 | — | ~128MB |

## وابستگی‌های مهم

```
matching_pack_gateway
    ├── ml_service ──────────────→ embedded_ai:8100 (EmbeddingClient داخلی)
    ├── embedded_ai ─────────────→ Redis
    ├── personality ─────────────→ /models/sentiment + /models/emotion (volume!)
    ├── ai_assistant ────────────→ Redis
    └── ai_support ──────────────→ /app/models (BERT فارسی، volume!)
```

## آماده‌سازی مدل‌ها (قبل از Deploy)

### personality مدل‌ها
```bash
# روی سرور:
python3 -c "
from transformers import AutoTokenizer, AutoModelForSequenceClassification
# sentiment
AutoTokenizer.from_pretrained('HooshvareLab/bert-fa-base-uncased-sentiment-snappfood').save_pretrained('./models/sentiment')
AutoModelForSequenceClassification.from_pretrained('HooshvareLab/bert-fa-base-uncased-sentiment-snappfood').save_pretrained('./models/sentiment')
# emotion (مثال — مدل واقعی رو از کدت چک کن)
AutoTokenizer.from_pretrained('your-emotion-model').save_pretrained('./models/emotion')
AutoModelForSequenceClassification.from_pretrained('your-emotion-model').save_pretrained('./models/emotion')
"
```

### ai_support مدل
```bash
python3 -c "
from transformers import pipeline
p = pipeline('sentiment-analysis', model='HooshvareLab/bert-fa-base-uncased-sentiment-snappfood')
p.save_pretrained('./support_models')
"
```

## Deploy

```bash
docker-compose -f docker-compose.yml \
               -f docker-compose.matching-pack.yml up -d matching_pack_gateway
```

## ساخت License Key

```bash
curl -X POST http://localhost:9003/admin/license/create \
  -H "X-Admin-Token: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain": "customer.com", "plan": "pro", "expires": "2027-01-01"}'
```

## Endpoints

| Endpoint | سرویس | عملکرد |
|----------|-------|--------|
| `POST /match/embed` | ml_service | embed کاربر + cache Redis |
| `POST /match/recommend` | ml_service | پیشنهاد بهترین matches |
| `POST /match/predict` | ml_service | match score دو کاربر |
| `POST /match/track-events` | ml_service | track رویداد |
| `POST /embed/text` | embedded_ai | embed یه متن |
| `POST /embed/batch` | embedded_ai | embed دسته‌ای |
| `POST /embed/similarity` | embedded_ai | cosine similarity |
| `POST /personality/sentiment` | personality | تحلیل sentiment |
| `POST /personality/emotion` | personality | تشخیص emotion |
| `POST /assistant/analyze` | ai_assistant | آنالیز کامل کاربر |
| `GET  /assistant/advice/{id}` | ai_assistant | توصیه‌های بهبود |
| `POST /assistant/chat` | ai_assistant | چت با دستیار |
| `POST /support/analyze` | ai_support | آنالیز تیکت |
| `GET  /support/tickets/{id}/analysis` | ai_support | تحلیل cache شده |
| `POST /support/feedback` | ai_support | فیدبک تیکت |
| `GET  /support/seo-insights` | ai_support | SEO از تیکت‌ها |
| `GET  /health` | gateway | وضعیت همه |

## خلاصه ۴ پک

| پک | Gateway | Port | سرویس‌ها |
|----|---------|------|---------|
| SEO Pack | :9000 | ✅ | ai_seo, aeo_tracker, ai_backlink, ai_seo_recommender |
| Safety Pack | :9001 | ✅ | ai_moderation, ai_verification, ai_image |
| Revenue Pack | :9002 | ✅ | ai_monetization, ai_revenue, ai_uplift, ai_feedback |
| Matching Pack | :9003 | ✅ | ml_service, embedded_ai, personality, ai_assistant, ai_support |
