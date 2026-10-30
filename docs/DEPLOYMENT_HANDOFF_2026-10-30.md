# Yarsalam deployment handoff — 2026-10-30

این سند برای ادامهٔ کار در چت جدید است. قبل از هر اقدام، این فایل و لینک‌های ارجاع‌شده را مبنا قرار بده؛ از کاربر نخواه تاریخچه را دوباره توضیح دهد.

## اصل قطعی استقرار

- سورس، تست، مستندات، Dockerfile، اسکریپت‌های build و فایل‌های توسعه فقط در GitHub نگهداری می‌شوند.
- روی VPS هیچ Git checkout، سورس کامل، تست، مستندات، wheelhouse یا build context غیرضروری نگهداری نمی‌شود.
- Build در GitHub Actions یا محیط Build خارج از VPS انجام می‌شود.
- VPS فقط Docker imageهای نهایی runtime، فایل‌های حداقلی Compose/تنظیمات اجرا، secrets خارج از Git/Image، داده‌های پایدار و volumeهای مدل را نگه می‌دارد.
- روی VPS دستور `docker compose build`، `up --build` یا build از سورس اجرا نشود.
- برای استقرار imageهای تازه از tag غیرقابل‌تغییر SHA یا digest استفاده شود؛ به `latest` برای تصمیم production تکیه نشود.
- عملیات هر Pack باید مستقل و محدود به همان Pack باشد. از `down -v`, `docker volume prune`, `docker system prune --volumes` و حذف volumeهای mobApp اجتناب شود.
- VPS فعلاً حدود 7.8 GiB RAM دارد؛ Packها یک‌به‌یک روشن و آزموده شوند، نه همگی هم‌زمان.

## AI Packs — نتایج واقعی و وضعیت فعلی

مخزن: [yarsalam/ai-packs](https://github.com/yarsalam/ai-packs)

شاخهٔ مبنای بسته‌بندی/استقرار: `feat/safety-ghcr-deployment`

شاخهٔ فعلی اصلاح محدود: `fix/matching-ai-assistant-runtime-image`

گزارش Smoke Test چهار Pack در 2026-10-29:
[`docs/LIVE_SMOKE_RESULTS_2026-10-29.md`](https://github.com/yarsalam/ai-packs/blob/feat/safety-ghcr-deployment/docs/LIVE_SMOKE_RESULTS_2026-10-29.md)

نتیجهٔ ثبت‌شده در آن گزارش:
- SEO: Runtime PASS؛ قابلیت URL Audit عمومی هنوز به egress firewall برای جلوگیری از SSRF/DNS rebinding نیاز دارد.
- Safety: Runtime PASS؛ نتیجه به‌تنهایی کیفیت مدل یا مجوز تجاری را ثابت نمی‌کند.
- Revenue: تمام بررسی‌های runtime موفق؛ اسکریپت به‌دلیل شکاف قابلیت‌ها exit 2 داده، چون `ai_revenue.model_trained=false`, `cv_score=0.0` و `ai_uplift.model_trained=false`. این خطای build/runtime محسوب نمی‌شود.
- Matching: Runtime PASS با imageها و مدل/volumeهای محلی موجود؛ fresh install از صفر در آن آزمون ثابت نشده بود.

کاربر تأیید کرده در دور Build/بررسی اخیر همهٔ Packها مثبت بوده‌اند و فقط `ai_assistant` خطا داشته است. در لاگ 2026-10-30 سرویس‌های Matching شامل `ai_support`, `matching_embedded_ai`, `ml_service`, `personality` و Redis سالم بودند. در وضعیت ثبت‌شده، سایر Packها هنگام orchestration با exit 143 متوقف شده‌اند؛ این کد shutdown است و نباید به‌اشتباه خطای build تعبیر شود. SEO بعداً با همهٔ سرویس‌ها Healthy بازیابی شده بود.

### خطای قطعی ai_assistant

Image معیوب قبلی:
`ghcr.io/yarsalam/ai-packs/matching-pack-ai-assistant:sha-9f114ff40fa4d628c8c0a8fa0f62032b09276d8e`

لاگ دقیق:
`ModuleNotFoundError: No module named 'pandas'`

زنجیرهٔ import:
`/app/app.py` → `api.assistant` → `core.behavior.py` → `import pandas as pd`

علت تأییدشده:
- در نسخهٔ builder مورد استفاده برای image قبلی، تعریف `SERVICE["ai_assistant"]["requirements"]` برابر `CORE + TORCH_CPU` بود و pandas نداشت.
- در builder شاخهٔ `feat/safety-ghcr-deployment` اصلاح انجام شده: `CORE + TORCH_CPU + ["pandas==2.2.3"]`.
- منبع فعلی `core/behavior.py` واقعاً از pandas و `pandas.DataFrame` استفاده می‌کند.

بنابراین اصلاح موردنیاز، Build و انتشار **فقط image ai_assistant** است؛ باقی Matching services یا سه Pack دیگر نباید مجدداً Build یا بی‌دلیل جایگزین شوند.

### نتیجهٔ CI در 2026-10-30

- PR #4: https://github.com/yarsalam/ai-packs/pull/4 — Draft/open، base=`feat/safety-ghcr-deployment`، head commit=`eb6875f7cab6573c390b7eea402d336e23c8659b`.
- PR #5: https://github.com/yarsalam/ai-packs/pull/5 — Draft/open، base=`main`؛ فقط ثبت workflow_dispatch روی شاخهٔ پیش‌فرض، بدون Build/Publish.
- Workflow run #53، ID `41118292186` — SUCCESS: ساخت چهار توزیع مستقل، Gateway contract checks، Validate ساختار/Compose و Build gateway images. مرحلهٔ افزودن ZIPها به GitHub Release skipped بوده، چون release event اجرا نشده؛ این شکست نیست.
- Workflow run #77، ID `41118292374` — SUCCESS: چهار Gateway contract test همگی موفق؛ توزیع Matching با فیلتر runtime ساخته و validate شد؛ Compose override معتبر بود؛ فقط Image `ai_assistant` build شد و importهای `pandas`, `app`, `core.behavior.analyze_behavior` در خود Image با موفقیت اجرا شدند.
- Image جدید فقط در Runner ساخته و import-tested شده است. در این CI هیچ GHCR push، pull از VPS، restart یا تغییر volume انجام نشد.

### Workflow اضافه‌شده در این شاخه

فایل: `.github/workflows/publish-matching-ai-assistant.yml`

کارکرد:
- فقط دستی با workflow_dispatch اجرا می‌شود.
- مخزن ai-packs و ref دقیق mobApp را checkout می‌کند.
- توزیع Matching را در محیط GitHub Actions می‌سازد و validate می‌کند. `build_distributions.py` فایل‌ها/پوشه‌های test، docs، cache، env، secret و Git metadata را از هر service context کنار می‌گذارد و validator این موارد را رد می‌کند.
- وجود `pandas==2.2.3` را هم در mapping builder و هم requirements تولیدشده بررسی می‌کند.
- فقط Image سرویس `ai_assistant` را Build می‌کند.
- داخل Image، `import pandas`, `import app` و import تابع `analyze_behavior` را بررسی می‌کند.
- فقط همان Image را با tag immutable شامل SHA مخزن ai-packs و SHA مخزن mobApp در GHCR منتشر می‌کند.
- هیچ سرویس یا فایلی روی VPS را تغییر نمی‌دهد.

ورودی `mobapp_ref` اکنون روی commit ثابت `93bcb0d9ddf78ed31580d4aa2e3758b6397c1f0b` pin شده است؛ همان base commit که در مقایسهٔ شاخهٔ `fix/ai-pack-commercial-readiness` با main تأیید شد. Workflow SHA دقیق checkoutشده را نیز در خروجی چاپ می‌کند.

### Compose برای جایگزینی محدود image

فایل: `deploy/compose/matching-ai-assistant-override.yaml`

این override تنها Image سرویس `ai_assistant` را به `AI_ASSISTANT_IMAGE` تنظیم می‌کند. Compose اصلی Matching و tagهای image بقیه سرویس‌ها را تغییر نمی‌دهد.

پس از انتشار image و فقط پس از تأیید کاربر، الگوی deploy محدود روی VPS:
```bash
docker compose --env-file "$ENV_FILE" -p yarsalam-matching-pack \
  -f matching-pack.json -f matching-ai-assistant-override.yaml pull ai_assistant

docker compose --env-file "$ENV_FILE" -p yarsalam-matching-pack \
  -f matching-pack.json -f matching-ai-assistant-override.yaml \
  up -d --no-deps ai_assistant
```
فایل env خصوصی باید شامل `AI_ASSISTANT_IMAGE=<tag دقیق منتشرشده>` باشد. مسیر Compose/env روی سرور باید با مسیر واقعی فایل‌های deployment control موجود تطبیق داده شود؛ مسیر یا فایل جدیدی را حدس نزن. این دستورات فقط الگو هستند، اجرا نشده‌اند.

سپس:
- وضعیت health کانتینر `ai_assistant` و لاگ آن بررسی شود.
- gateway matching و درخواست‌های واقعی از مسیر آن بررسی شوند.
- سرویس‌های سالم دیگر دست‌نخورده باقی بمانند.
- اگر نیاز به rollback ایجاد شد، ابتدا image قبلی/جدید و وضعیت volumeها ثبت و یک تصمیم صریح گرفته شود؛ image قبلی فاقد pandas است و rollback به آن، خطای شناخته‌شده را برمی‌گرداند.

## PRهای Runtime-only تکمیلی (2026-10-30)

- پنل ادمین: PR #31 https://github.com/yarsalam/admin-panel/pull/31 — Next.js standalone، multi-stage runtime-only image، Docker context filtering و Compose image-only؛ Draft/open، head فعلی `0c5aaebbc789af145e3f2852ed2ed591b907876c` و هنوز CI اجرا نشده. PR #32 https://github.com/yarsalam/admin-panel/pull/32 — ثبت stubهای دستی validation/publish در main؛ Draft/open. فایل env موجود روی سرور `.env` است (نه `.env.production`)، و Compose/راهنمای PR31 با آن هماهنگ شده‌اند.
- Backend اصلی mobApp: PR #8 https://github.com/yarsalam/mobApp/pull/8 — Compose مستقل با فقط Image سرویس backend، network خارجی موجود و حفظ مسیر public assets با PUBLIC_ASSETS_DIR؛ Draft/open، head فعلی `ce8754ff35bfb7cf02161a3bc62a1d93f4beaa54` و base آن شاخهٔ feat/ci-runtime-backend-image است.
- برای هیچ‌یک از این سه PR هنوز Image نهایی GHCR منتشر یا روی VPS Deploy نشده است.
- روی VPS فعلاً فقط باید runtime artifacts، Compose حداقلی و env خصوصی باقی بمانند؛ سرویس‌ها و داده‌های موجود قبل از هر replacement با docker inspect بررسی شوند.

## وضعیت PRهای مرتبط

### ai-packs
- PR #1: `Harden AI Pack licensing and add commercialization audit` — باز و Draft؛ پایهٔ commercialization/readiness.
- PR #2: `Add GHCR image deployment workflow for Safety Pack` — باز و Draft؛ شاخهٔ feature شامل workflowها و Composeهای image-only برای همهٔ Packهاست.
- PR #3: ثبت workflow_dispatch در main — بسته شده/ادغام شده، اما workflowهای main فقط registration stub هستند؛ برای Build/Publish واقعی باید شاخهٔ feature انتخاب شود.
- اصلاح محدود ai_assistant روی شاخهٔ اختصاصی این سند انجام شده و PR آن باید به `feat/safety-ghcr-deployment` هدف‌گذاری شود. CI موجود در شاخهٔ feature نیز Build/Import-check فقط ai_assistant را انجام می‌دهد. چون publisher در main هنوز به‌صورت registration stub ثبت نشده، یک PR جداگانه برای ثبت dispatch در main لازم است. تا زمان merge و بررسی، publish دستی انجام نشود.

### mobApp
- PR #4: runtime-only Backend image و GH Actions؛ باز.
- PR #5: سخت‌سازی Dockerfile/backend و Recaptcha startup؛ بسته شده.
- PR #6: سخت‌سازی Python serviceها و تست readiness؛ باز/Draft.
- PR #7: SEO public URL audit؛ باز.
- برای Matching source، شاخهٔ `fix/ai-pack-commercial-readiness` در زمان بررسی 24 commit جلوتر از main و بدون عقب‌ماندگی بود. از این شاخه برای Build استفاده شده، اما هنگام اجرای Workflow باید SHA دقیق واقعی ثبت شود.
- Compose تولیدی اصلی mobApp هنوز از Compose توسعه‌ای ارث می‌برد و سرویس‌های متعدد `build:` دارد؛ باید در PR مستقل به runtime-only Compose حداقلی تبدیل شود، بدون حذف دیتابیس/Redis/Qdrant یا volumeهای موجود.

### admin-panel
- PR #30 `fix(auth): restore form submission in production admin auth` ادغام شده است.
- Base branch: `feat/production-deployment-memory`
- Merge commit: `734ef06b72bdd37899570defe339b4406efc40dc`
- فقط سه فرم login/register/set-password صریحاً `type="submit"` گرفتند.
- PR #29 روی base متفاوت بود و نباید برای انتشار production انتخاب شود.
- Dockerfile production پنل ادمین هنوز با `COPY . .` سورس Monorepo را داخل Build می‌برد و Next standalone فعال نشده است. نیاز به pipeline و Image runtime-only مستقل دارد.
- TypeScript/lint/build محلی قبلی که خطای favicon داشتند، روی branch اشتباه PR #29 اجرا شده بودند؛ آن نتایج را به‌عنوان شکست PR #30 گزارش نکن. نسخهٔ Mergeشده باید جداگانه validate شود.

## کارهای باز به ترتیب

1. PR محدود ai_assistant را به `feat/safety-ghcr-deployment` باز کن و CI Build/Import-check آن را سبز کن. فایل publisher فقط دستی و فقط برای ai_assistant publish می‌کند.
2. PR #4 اصلاح ai_assistant و PR #5 ثبت workflow_dispatch را review کن. بعد از تأیید/merge لازم، در Actions شاخهٔ `fix/matching-ai-assistant-runtime-image` را انتخاب و publisher را با MobApp SHA ثابت اجرا کن. انتظار tag از شکل `sha-<AI_PACKS_SHA>-mobapp-93bcb0d9ddf7` است؛ مقدار کامل را فقط از خروجی Workflow بردار.
3. صحت GHCR package visibility/authentication را از VPS بررسی کن؛ در صورت نیاز به ارتباط خارجی از VPN استفاده شود. تا پیش از انتشار، روی VPS چیزی تغییر نده.
4. پس از انتشار موفق و تأیید کاربر، فقط image مربوط به ai_assistant را با override و `--no-deps` جایگزین کن.
5. سپس برای mobApp و admin-panel، Build خارج از VPS، runtime-only image و Compose image-only را تکمیل کن. هرکدام PR و اعتبارسنجی جدا داشته باشند.
6. در پایان فایل‌های handoff را با commit SHAها، نتایج CI، image tags/digests و وضعیت دقیق VPS به‌روزرسانی کن.

## محدودیت عملیات

هیچ‌یک از workflowهای انتشار دستی در این مرحله اجرا نشده‌اند؛ هیچ Image جدیدی در GHCR publish نشده و هیچ سرویس/volume/VPS تغییر داده نشده است. Merge و deployment صرفاً پس از بررسی/تأیید صریح انجام شود.
