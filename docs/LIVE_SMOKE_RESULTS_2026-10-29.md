# نتایج Smoke Test محلی چهار AI Pack — ۲۹ اکتبر ۲۰۲۶

## دامنه و محدودیت شواهد

این گزارش نتیجهٔ اجرای زندهٔ `scripts/smoke_test_packs.py` روی توزیع‌های محلی زیر `~/ai-packs/dist` در کامپیوتر توسعه‌دهنده را ثبت می‌کند. این نتایج، CI، ساخت کاملاً تمیز از مخزن، نصب از صفر روی ماشین مشتری، اجرای production یا benchmark کیفیت مدل نیستند.

برای استفاده از imageها و مدل‌های موجود، Compose override و Dockerfileهای محلی استفاده شدند. هیچ فایل `.env`، توکن مدیریت، رمز Redis یا کلید مجوزی در Git ثبت نشده است. هیچ تغییری روی VPS یا production با این تست‌ها انجام نشده است.

## خلاصهٔ نتایج

| Pack | Runtime result | شواهد اصلی | وضعیت انتشار طبق گزارش |
|---|---|---|---|
| SEO | PASS | health، ساخت/اعتبارسنجی/revoke مجوز، audit HTML وب‌سایت عمومی، شباهت موضوعی embedding و usage موفق | NOT_READY_FOR_PUBLIC_SALE؛ برای URL audit عمومی، محدودیت egress در لایهٔ شبکه برای مقابله با SSRF/DNS rebinding لازم است |
| Safety | PASS؛ کد خروجی 0 | همهٔ ۷ بررسی: health تمام سرویس‌ها، مجوز، moderation معنایی متن فارسی، قاعدهٔ عبارت ممنوعه، usage و revoke موفق | REVIEW_REQUIRED؛ این Smoke Test کیفیت مدل، false-positive/false-negative یا آمادگی حقوقی را ارزیابی نمی‌کند |
| Revenue | PASS؛ کد خروجی 2 به‌علت شکاف قابلیت | همهٔ بررسی‌های runtime موفق؛ promotion endpoint چهار candidate را پاسخ داد؛ مجوز و usage موفق | NOT_READY_FOR_PUBLIC_SALE؛ health اعلام کرد `ai_revenue.model_trained=false`، `cv_score=0.0` و `ai_uplift.model_trained=false` |
| Matching | PASS؛ کد خروجی 0 | health، مجوز، embedding چندزبانه با بردار 384بعدی، دو پیش‌بینی sentiment، usage و revoke موفق | REVIEW_REQUIRED؛ benchmark کیفیت، ارزیابی خطا، مجوز مدل‌ها و بررسی نصب تمیز هنوز مستقل هستند |

### SEO Pack

در اجرای محلی، URL audit با وضعیت HTTP موفق، عنوان موجود و ۱۱ چک برگشت؛ topical similarity برابر حدود `0.84657` بود. با این حال، برنامه به‌تنهایی نمی‌تواند DNS rebinding را به‌طور کامل متوقف کند. دسترسی عمومی این قابلیت باید پشت egress firewall/network policy باشد که loopback، شبکه‌های خصوصی و metadata endpointها را مسدود کند.

باگ import محلی در `create_license` نیز در همین شاخه اصلاح شده است: import داخلی `json, secrets` به `json` تغییر کرد تا از سایه‌اندازی نام `secrets` و `UnboundLocalError` جلوگیری شود. این اصلاح در توزیع local و در فایل source مربوط به SEO باید هم‌خوان باشد.

### Safety Pack

برای اجرای محلی از image قدیمی `backend-ai_image:latest` استفاده شده بود که `nudenet` را نداشت؛ سرویس با image محلی اصلاح‌شده بالا آمد و تست کامل پاس شد. در سازندهٔ توزیع‌های مخزن، `nudenet==3.4.2` از قبل در requirements تعریف شده است. بنابراین اجرای clean build از ابزار سازنده همچنان لازم است تا تطابق image نهایی با dependencies اعلام‌شده ثابت شود.

### Revenue Pack

Gateway محلی با `httpx==0.27.0` ساخته شد، چون image پایهٔ استفاده‌شده برای تست محلی این dependency را نداشت؛ `httpx` در requirements خود Gateway تعریف شده است. پاسخ موفق promotion endpoint به‌تنهایی نشان‌دهندهٔ مدل آموزش‌دیده یا کالیبره نیست. پیش از فروش، باید مدل‌های Revenue و Uplift با دادهٔ مجاز و نماینده آموزش/اعتبارسنجی شوند و ارزیابی مستقل/زمانی گزارش شود.

### Matching Pack

برای جلوگیری از دانلود مجدد در اجرای محلی، مدل MiniLM از مسیر محلی mount شد، volume موجود `yarsalam-project_personality_models` استفاده شد و `model_init` در override محلی فقط بررسی موفقیت محتوای موجود را شبیه‌سازی کرد. در نتیجه، Smoke Test ثابت می‌کند سرویس‌ها با این مدل‌های محلی قابل‌دسترسی‌اند؛ ثابت نمی‌کند fresh install، دانلود نسخه‌بندی‌شدهٔ مدل‌ها یا فرایند model-init از صفر موفق است.

## تصمیم اجرایی

- هر چهار Pack اکنون یک اجرای محلی با `runtime_status: PASS` ثبت‌شده دارند.
- این وضعیت را به معنی «چهار محصول آمادهٔ فروش» تفسیر نکنید.
- SEO برای انتشار URL audit عمومی به network egress controls نیاز دارد.
- Revenue قبل از ادعای کیفیت یا فروش مبتنی بر پیش‌بینی، به آموزش، ارزیابی و کالیبراسیون مدل‌های Revenue/Uplift نیاز دارد.
- برای Safety و Matching، benchmark مدل، تحلیل خطا، مجوزهای مدل/وابستگی، تست بار/امنیت و fresh install هنوز دروازه‌های جدا هستند.
- مرحلهٔ بعد باید clean build از هر چهار توزیع با `build_distributions.py` و `validate_distributions.py` و سپس آزمون install-from-zero باشد؛ overrideهای محلی این گزارش را در بستهٔ مشتری یا production کپی نکنید.
