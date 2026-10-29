# YarSalam AI Packs

چهار محصول AI با API یکپارچه و افزونه‌های WordPress. این مخزن Gatewayها، افزونه‌ها و ابزار ساخت توزیع‌ها را نگه می‌دارد؛ کد اصلی سرویس‌های Python در [yarsalam/mobApp](https://github.com/yarsalam/mobApp) نگه‌داری می‌شود.

**وضعیت فعلی: preview فنی، نه محصول تجاری تأییدشده.** قبل از فروش عمومی باید build و CI، مجوز مدل‌ها، benchmark کیفیت، هزینهٔ واقعی inference و آزمون امنیت/بار تأیید شوند.

- [ارزیابی فنی و تجاری](./docs/PRODUCT_AUDIT_2026-10-28.md)
- [نقشهٔ راه تجاری‌سازی](./docs/COMMERCIALIZATION_ROADMAP.md)
- [منشأ مدل‌ها و شروط انتشار تجاری](./docs/MODEL_PROVENANCE.md)
- [راهنمای آزمون زندهٔ چهار پک](./docs/LIVE_SMOKE_TESTING.md)
- [نتایج Smoke Test محلی چهار پک — ۲۹ اکتبر ۲۰۲۶](./docs/LIVE_SMOKE_RESULTS_2026-10-29.md)

## چهار پک

| پک | چه کاری انجام می‌دهد | سرویس‌های اصلی |
|---|---|---|
| SEO Pack | پیش‌بینی ترافیک، پایش حضور برند در پاسخ‌های AI، تحلیل لینک و پیشنهاد SEO | ai_seo, aeo_tracker, ai_backlink_quality, ai_seo_recommender |
| Safety Pack | moderation متن، بررسی تصویر و تطبیق چهره | ai_moderation, ai_image, ai_verification |
| Revenue Pack | تحلیل promotion، LTV، uplift و feedback تبدیل | ai_monetization, ai_revenue, ai_uplift, ai_feedback |
| Matching Pack | embedding، matching، تحلیل احساس/شخصیت و AI support | ml_service, embedded_ai, personality, ai_assistant, ai_support |

## تولید بسته‌های قابل‌نصب

فایل‌های Compose زیر پوشه‌های pack در این مخزن برای توسعهٔ داخلی نگه‌داری می‌شوند. آن‌ها به‌تنهایی توزیع مشتری نیستند. بستهٔ قابل‌نصب باید با ابزار سازنده تولید شود؛ این کار کدهای لازم را از mobApp داخل خروجی کپی می‌کند، برای هر سرویس Dockerfile مستقل می‌سازد و Compose/افزونهٔ WordPress را همراه خروجی قرار می‌دهد.

پیش‌نیاز: checkout از هر دو مخزن در کنار هم و Python 3.11 یا جدیدتر.

    git clone https://github.com/yarsalam/ai-packs.git
    git clone https://github.com/yarsalam/mobApp.git
    python -m pip install PyYAML==6.0.2
    python ai-packs/scripts/build_distributions.py --mobapp-root mobApp --output-dir ai-packs/dist
    python ai-packs/scripts/validate_distributions.py --dist-dir ai-packs/dist

در خروجی، برای هر پک یک پوشهٔ مستقل، ZIP توزیع و ZIP افزونهٔ WordPress ساخته می‌شود. فایل‌های مدل حجیم داخل git قرار نمی‌گیرند؛ مدل‌ها در زمان نصب دانلود می‌شوند. این به دسترسی شبکه و فضای دیسک نیاز دارد. برای Matching، مدل‌های فارسی sentiment و emotion از یک مرحلهٔ init دانلود می‌شوند.

همچنین workflow [Build self-contained AI Pack distributions](./.github/workflows/distributions.yml) خروجی‌ها را روی Pull Request اعتبارسنجی می‌کند و هنگام انتشار GitHub Release فایل‌های ZIP را به Release پیوست می‌کند. در محیط فعلی، خروجی باید همچنان به‌عنوان preview تلقی شود تا build کامل هر سرویس مدل‌محور و تست واقعی inference هم انجام شود.

## نصب در سرور مشتری

از ZIP همان پک استفاده کنید، نه Compose توسعه‌ای این مخزن. در پوشهٔ بسته:

    cp .env.example .env
    openssl rand -hex 32
    docker compose --env-file .env up -d --build

دو راز قوی و جداگانه برای REDIS_PASSWORD و توکن مدیریت همان پک قرار دهید. مقادیر CHANGE_ME را نگه ندارید. پورت Gateway به‌صورت پیش‌فرض فقط روی 127.0.0.1 منتشر می‌شود؛ برای دسترسی عمومی، reverse proxy با HTTPS تنظیم کنید.

برای صدور کلید آزمایشی، endpoint مدیریتی همان Gateway با هدر X-Admin-Token استفاده می‌شود. درخواست‌های مشتری باید X-License-Key را در header بفرستند. **کلید License/Admin را داخل JavaScript مرورگر، اپ موبایل یا query string قرار ندهید.**

## طرح استفاده و وضعیت تجاری

- endpoint مربوط به GET /usage، مصرف credit ساعتی/ماهانه را نشان می‌دهد؛ وزن عملیات و سهمیه‌های فعلی پیش‌فرض آزمایشی‌اند و هنوز بر اساس هزینهٔ واقعی inference و پایلوت مشتری تنظیم نشده‌اند.
- آموزش مدل فقط برای پلن‌های Pro و Enterprise مجاز است؛ این هنوز صورتحساب خودکار نیست.
- صدور/لغو مجوز فعلاً از endpoint مدیریت انجام می‌شود. درگاه پرداخت، پنل مشتری، تمدید خودکار، صدور خودکار بعد از پرداخت و پشتیبانی/SLA تجاری هنوز پیاده‌سازی نشده‌اند.
- ادعای دقت، کاهش تقلب یا افزایش درآمد را تا انتشار benchmark مستقل و پایلوت کنترل‌شده مطرح نکنید.
- قبل از توزیع عمومی، مجوز هر بستهٔ Python و مدل از پیش‌آموزش‌دیده، شرایط پردازش داده و سیاست نگه‌داری/حذف را بازبینی کنید.

## توسعه و تست

- Gatewayها و افزونه‌ها: همین مخزن.
- میکروسرویس‌های اصلی و تست رگرسیون آمادگی بسته‌ها: [mobApp PR](https://github.com/yarsalam/mobApp/pull/6).
- اصلاحات gateway، قرارداد license، quota و ابزار بسته‌بندی: [ai-packs PR](https://github.com/yarsalam/ai-packs/pull/1).

تا زمانی که هر دو PR بازبینی و ادغام نشده‌اند، CI سبز نباشد و آزمون end-to-end مدل‌ها اجرا نشده باشد، این تغییرات را روی production deploy نکنید.
