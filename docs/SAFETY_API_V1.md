# Safety Pack — API contract v1 (preview)

این سند قرارداد اولیهٔ Gateway تجاری است. پاسخ‌ها برای integration و پایلوت فنی طراحی شده‌اند، نه ادعای دقت تأییدشده.

## Authentication

همهٔ مسیرهای محافظت‌شده از هدر `X-License-Key` استفاده می‌کنند. کلید را در query string، کد frontend یا اپ موبایل قرار ندهید. `X-Admin-Token` فقط برای عملیات مدیریت و صدور/لغو مجوز در backend امن است.

## Tenant policy

### GET /policy

سیاست tenant مربوط به همان License را برمی‌گرداند. اگر سیاستی ثبت نشده باشد، مقادیر پیش‌فرض امن بازگردانده می‌شوند.

### PUT /policy

نمونهٔ درخواست:

```json
{
  "default_action": "review",
  "category_actions": {
    "external_contact": "review",
    "commercial_spam": "review",
    "violence": "block",
    "semantic_violation": "review",
    "policy_violation": "review",
    "text_length": "block",
    "unknown": "review"
  },
  "blocked_terms": ["عبارت قطعاً ممنوع"],
  "review_terms": ["عبارت نیازمند بررسی"]
}
```

- action فقط یکی از `allow`, `review`, `block` است.
- حداکثر ۱۰۰ عبارت برای هر فهرست، با طول ۲ تا ۸۰ نویسه پذیرفته می‌شود.
- حروف عربی/فارسی رایج، اعداد فارسی/عربی و نویسه‌های نامرئی رایج برای تطبیق نرمال می‌شوند.
- عبارت‌های blocked پیش از سیگنال مدل بررسی می‌شوند؛ عبارت‌های review نیز نتیجه را به صف بررسی انسانی هدایت می‌کنند.
- allow list برای override کردن تشخیص مدل عمداً در v1 وجود ندارد.

## Moderation decision

### POST /moderate/decision

درخواست:

```json
{
  "text": "بیا ادامه صحبت رو بیرون از اپ در واتساپ انجام بدیم",
  "context": "message"
}
```

محدودهٔ context: `message`, `bio`, `comment`, `profile`.

پاسخ نمونه:

```json
{
  "action": "review",
  "allowed": false,
  "review_required": true,
  "blocked": false,
  "category": "external_contact",
  "reason": "banned_keyword",
  "evidence": "واتساپ",
  "policy_version": 1,
  "model_signal": {
    "layer": "rule",
    "confidence": 1.0,
    "reason": "banned_keyword"
  },
  "context": "message",
  "checked_at": "2026-11-02T..."
}
```

معانی:
- `allow`: طبق مدل/سیاست فعلی اجازهٔ عبور دارد.
- `review`: قبل از اقدام نهایی، بررسی انسانی لازم است.
- `block`: طبق سیاست tenant مسدود شود.

اگر embedding/سرویس معنایی در دسترس نباشد یا upstream `review_required` برگرداند، تصمیم به‌اجبار `review` خواهد بود؛ تنظیم `default_action` نمی‌تواند این fail-safe را به allow یا block تبدیل کند.

## محدودیت‌های شناخته‌شده

- نرمال‌سازی فعلی transliteration فینگلیش یا فهم زبان‌شناختی slang را انجام نمی‌دهد.
- تشخیص معنایی فعلی بر embedding و مثال‌های محدود upstream متکی است؛ confidence آن احتمال کالیبره‌شده نیست.
- کلیدواژه‌های upstream ممکن است در بعضی contextها false positive ایجاد کنند؛ به همین علت پیش‌فرض دسته‌های مبهم review است.
- این نسخه هنوز صف بازبینی، appeal، role management، audit log مدیریتی، webhook و dashboard عملیاتی ندارد.
- سهمیه‌های credit آزمایشی هستند و هنوز براساس هزینهٔ واقعی inference تنظیم نشده‌اند.
- متن درخواست در Gateway ذخیره نمی‌شود؛ پیش از فروش باید رفتار لاگ و cache تمام سرویس‌های پایین‌دست هم audit شود.

این API باید روی مجموعهٔ فارسیِ دارای مجوز benchmark شود. انتشار precision/recall/F1 و نرخ false-positive/false-negative برای هر دسته پیش‌شرط ادعای کیفیت است.

## بررسی دسته‌ای

### POST /moderate/batch/decision

حداکثر ۱۰۰ متن در یک درخواست؛ هر متن حداکثر ۲٬۰۰۰ نویسه:

```json
{
  "context": "comment",
  "texts": [
    "سلام، وقت بخیر",
    "لطفاً در واتساپ پیام بده"
  ]
}
```

پاسخ تعداد تصمیم‌ها و نتیجهٔ هر index را می‌دهد. متن‌ها در Gateway در صف یا دیتابیس ذخیره نمی‌شوند. سهمیهٔ درخواست دسته‌ای بر اساس وزن موقت آن محاسبه می‌شود.

## آمار ماهانهٔ حریم‌خصوصی‌محور

### GET /analytics/summary?period=2026-11

خروجی شامل تعداد کل، تعداد allow/review/block و شمارش بر اساس دسته است. فقط شمارنده‌های تجمیعی در Redis ذخیره می‌شوند و retention فعلی ۱۸۰ روز است. هیچ متن، شناسهٔ کاربر یا IP در این آمار وجود ندارد. این آمار، audit log یا صف بررسی انسانی نیست.
