# Yarsalam deployment handoff — 2026-10-30

این سند برای ادامهٔ کار در چت جدید است. قبل از هر اقدام، این فایل و لینک‌های ارجاع‌شده را مبنا قرار بده؛ از کاربر نخواه تاریخچه را دوباره توضیح دهد.

## دو مسئلهٔ اصلی و باز پروژه — حتماً در چت بعدی از همین‌جا ادامه بده

این پروژه در حال حاضر دو مسئلهٔ اصلی دارد؛ آن‌ها را با هم قاطی نکن و موضوع سومی را جایگزین اولویت‌ها نکن:

### مسئلهٔ ۱ — دکمهٔ «ورود» پنل مدیریت کار نمی‌کند

- علت فنی پیدا شد: در تغییر `29500931852a0366294397ffdf4e3fcef93e7261` پیش‌فرض `CustomButton` به `type="button"` تغییر کرده بود، در حالی که فرم Login صریحاً `type="submit"` نداشت؛ در نتیجه کلیک فرم را submit نمی‌کرد.
- اصلاح کد در PR #30 مخزن `yarsalam/admin-panel` ادغام شده است: `734ef06b72bdd37899570defe339b4406efc40dc`. فرم‌های login/register/set-password اکنون صریحاً submit هستند.
- **این اصلاح هنوز روی VPS منتشر نشده است.** پس مسئلهٔ کاربر در Production تا زمان انتشار Image جدید و تعویض محدود سرویس `admin-web` حل‌شده تلقی نمی‌شود.
- PR #31: https://github.com/yarsalam/admin-panel/pull/31 — Image نهایی Next.js به شکل standalone/runtime-only، Compose فقط Image و Pipeline انتشار. CI run #4، شناسهٔ `41120657283`، موفق شده: Build Image، اجرای کانتینر آزمایشی و پاسخ HTTP 200 از `/login`، و بررسی نبودن `.git`، `.github` و docs در Image.
- خطای TypeScript صفحهٔ Safety در Build اول پیدا و با خارج‌کردن `RiskPanel` از فایل route و معتبرکردن props صفحه اصلاح شد. CI موفق مربوط به run #4 است؛ نتایج خطادار قبلی را نتیجهٔ نهایی تلقی نکن.
- PR #31 هنوز باید review/merge شود. Image هنوز به GHCR Push نشده و روی VPS Deploy نشده است. پس از تأیید کاربر، فقط `admin-web` با Image tag غیرقابل‌تغییر تعویض شود؛ Backend، DB، Redis، Nginx/proxy و برنامهٔ اصلی دست‌نخورده بمانند.
- PR #29 مبنای انتشار نیست؛ مبنای درست، شاخهٔ Production و PR #30 ادغام‌شده است.

### مسئلهٔ ۲ — سرویس `ai_assistant` در Matching خطا می‌دهد

- Image قبلی با tag `sha-9f114ff40fa4d628c8c0a8fa0f62032b09276d8e` به‌دلیل `ModuleNotFoundError: No module named 'pandas'` از کار می‌افتاد.
- علت و اصلاح مشخص شده: در requirements Image جدید `pandas==2.2.3` pin شده است.
- PR #4: https://github.com/yarsalam/ai-packs/pull/4 — اصلاح محدود Image، Build/Import test، Workflow دستی انتشار و Compose override تک‌سرویسی. این PR به شاخهٔ `feat/safety-ghcr-deployment` هدف‌گذاری شده، برای review آماده است و هنوز ادغام نشده.
- آخرین CI مربوط به اصلاح: run #83، شناسهٔ `41119988887`، موفق؛ فقط Image مربوط به `ai_assistant` ساخته و Importهای `pandas`، `app` و `core.behavior.analyze_behavior` داخل Image آزمایش شده‌اند. چهار تست Gateway licensing contract هم موفق‌اند.
- Build و validation توزیع‌ها در run #59، شناسهٔ `41119988888`، موفق شده است.
- **Image جدید هنوز در GHCR منتشر نشده و روی VPS نصب نشده است.** پس خطای Production هنوز تا استقرار واقعی باز است.
- راه‌حل مورد توافق: انتشار مجدد و جایگزینی **فقط Image مربوط به `ai_assistant`**. نه SEO، نه Safety، نه Revenue و نه چهار سرویس سالم دیگر Matching نباید دوباره Build یا روی VPS تعویض شوند. آن سرویس‌ها را دست‌نخورده حفظ کن.
- پس از review/merge و اجرای دستی publisher، tag دقیق و immutable خروجی را ثبت کن؛ سپس فقط سرویس `ai_assistant` را با override و `--no-deps` به‌روزرسانی کن.

## سه تصمیم قطعی معماری — در چت بعدی هم تغییر نده

1. سورس، تست‌ها، مستندات و فایل‌های توسعه فقط در GitHub نگهداری می‌شوند.
2. VPS فقط Imageهای نهایی Runtime، فایل‌های ضروری اجرای Production مانند Compose و تنظیمات، Secrets خصوصی و داده‌های پایدار/volumeهای لازم را نگه می‌دارد.
3. هیچ Build سورسی روی VPS انجام نمی‌شود؛ Build در GitHub Actions یا محیط خارج از VPS انجام می‌شود و فقط آرتیفکت نهایی (Image) به VPS منتقل یا از Registry دریافت می‌شود.

هر پیشنهاد یا دستور خلاف این سه تصمیم را رد کن. برای تغییر Production، Image immutable استفاده کن و فقط همان سرویس موردنظر را تغییر بده.

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

- PR #4: https://github.com/yarsalam/ai-packs/pull/4 — Open و Ready for review، base=`feat/safety-ghcr-deployment`، آخرین head ثبت‌شده=`40730df5112ee8140bfd215a7ddb26014f8fa75f`.
- PR #5: https://github.com/yarsalam/ai-packs/pull/5 — ادغام‌شده در `main` با commit `52dcab1f9a876bba5e2dd060917a79296251ffea`؛ فقط ثبت workflow_dispatch است و خودش Build/Publish نمی‌کند.
- Workflow run #53، ID `41118292186` — SUCCESS: ساخت چهار توزیع مستقل، Gateway contract checks، Validate ساختار/Compose و Build gateway images. مرحلهٔ افزودن ZIPها به GitHub Release skipped بوده، چون release event اجرا نشده؛ این شکست نیست.
- Workflow run #83، ID `41119988887` — SUCCESS: چهار Gateway contract test همگی موفق؛ توزیع Matching با فیلتر runtime ساخته و validate شد؛ Compose override معتبر بود؛ فقط Image `ai_assistant` build شد و importهای `pandas`, `app`, `core.behavior.analyze_behavior` در خود Image با موفقیت اجرا شدند. Run قبلی #77 نیز موفق بود.
- Image جدید فقط در Runner ساخته و import-tested شده است. در این CI هیچ GHCR push، pull از VPS، restart یا تغییر volume انجام نشد.

### Workflow اضافه‌شده در این شاخه

فایل: `.github/workflows/publish-matching-ai-assistant.yml`

کارکرد:
- فقط دستی با workflow_dispatch اجرا می‌شود.
- مخزن ai-packs و ref دقیق mobApp را checkout می‌کند.
- توزیع Matching را در محیط GitHub Actions می‌سازد و validate می‌کند. `build_distributions.py` فایل‌ها/پوشه‌های test، docs، cache، env، secret و Git metadata را از تمام Python service و Gateway contextها کنار می‌گذارد و validator این موارد را رد می‌کند.
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

- پنل ادمین: PR #31 https://github.com/yarsalam/admin-panel/pull/31 — Next.js standalone، multi-stage runtime-only image، Docker context filtering و Compose image-only؛ Open، هنوز نیازمند review/merge؛ CI run #4 با ID `41120657283` موفق است. PR #32 https://github.com/yarsalam/admin-panel/pull/32 — ثبت stubهای دستی validation/publish در `main`، ادغام‌شده با commit `38d59f2c77630768a3b13849e8fadea39a11790b`. فایل env موجود روی سرور `.env` است (نه `.env.production`). Image منتشر یا Deploy نشده؛ مشکل ورود Production همچنان باز است تا تعویض `admin-web`.
- Backend اصلی mobApp: PR #8 https://github.com/yarsalam/mobApp/pull/8 — Compose مستقل با فقط Image سرویس backend؛ Open. در run #4، اعتبارسنجی Compose پس از اصلاح env-file موفق است؛ Build Image موفق بوده، اما Trivy به‌خاطر آسیب‌پذیری‌های HIGH/CRITICAL در Image متوقف شده و هیچ Image منتشر نشده است. این مورد پیگیری فرعی است و نباید دو مسئلهٔ اصلی بالا را جابه‌جا کند.
- برای هیچ‌یک از این سه PR هنوز Image نهایی GHCR منتشر یا روی VPS Deploy نشده است.
- روی VPS فعلاً فقط باید runtime artifacts، Compose حداقلی و env خصوصی باقی بمانند؛ سرویس‌ها و داده‌های موجود قبل از هر replacement با docker inspect بررسی شوند.

## وضعیت فعلی Pull Requestها

### مخزن ai-packs
- PR #4 https://github.com/yarsalam/ai-packs/pull/4: اصلاح `ai_assistant`، آمادهٔ review، باز و هنوز merge نشده؛ base برابر `feat/safety-ghcr-deployment`. CI run #83 (`41119988887`) برای Build فقط Image همین سرویس و Import-test موفق شده است. run #59 (`41119988888`) نیز توزیع‌های چهار Pack و Gatewayها را با موفقیت ساخته است.
- PR #5 در `main` ادغام شده: `52dcab1f9a876bba5e2dd060917a79296251ffea`. این فقط registration stub است و خودش Image نمی‌سازد یا منتشر نمی‌کند.
- Image جدید `ai_assistant` هنوز به GHCR Push نشده است.

### مخزن admin-panel
- PR #30 ادغام شده: `734ef06b72bdd37899570defe339b4406efc40dc`; اصلاح submit فرم‌ها در کد انجام شده، ولی Production هنوز Deploy نشده.
- PR #31 https://github.com/yarsalam/admin-panel/pull/31: runtime-only/standalone Image و Compose فقط Image، باز و نیازمند review/merge. CI run #4 (`41120657283`) Build، اجرای کانتینر آزمایشی، HTTP 200 از `/login` و حذف Git metadata/docs از Image را تأیید کرده است. پس از run #4 یک commit کوچک `31989503311b4fab6867464d6ab432da76d87039` اضافه شد که `RiskPanel` را صریحاً Client Component می‌کند؛ CI باید روی این آخرین commit دوباره تأیید شود.
- PR #32 در `main` ادغام شده: `38d59f2c77630768a3b13849e8fadea39a11790b`. این فقط registration stub است.
- Image پنل ادمین هنوز به GHCR Push یا روی VPS Deploy نشده است.

### مخزن mobApp
- PR #8 https://github.com/yarsalam/mobApp/pull/8: Compose runtime-only با فقط سرویس backend، باز و نیازمند review.
- CI run #4 (`41120765566`): اعتبارسنجی Compose پس از اصلاح env-file موفق شد؛ Build Image موفق بود، اما Trivy به‌دلیل آسیب‌پذیری‌های HIGH/CRITICAL در OS و Node dependencies fail شد. Image به همین علت Push نشد.
- این مورد پیگیری فرعی است و نباید تمرکز دو مسئلهٔ اصلی (ورود پنل و ai_assistant) را جابه‌جا کند. scan را خاموش نکن و آسیب‌پذیری‌ها را نادیده نگیر.

## کارهای باز به ترتیب

1. مسئلهٔ ورود پنل را تا انتها پیگیری کن: PR #31 را review/merge کن، سپس بعد از تأیید کاربر Image ادمین را با publisher دستی و URL واقعی API بساز و منتشر کن؛ فقط `admin-web` را Deploy کن و Login واقعی را روی Production امتحان کن. تا قبل از Deploy، PR #30 را «اصلاح‌شده در کد» بدان، نه «حل‌شده در Production».
2. PR #4 مربوط به `ai_assistant` را review/merge کن؛ publisher دستی را با MobApp SHA ثابت اجرا کن و tag کامل خروجی را ثبت کن.
3. فقط پس از تأیید کاربر، Image `ai_assistant` را جایگزین کن؛ به هیچ Image سالم Matching یا SEO/Safety/Revenue دست نزن.
4. پس از هر انتشار، نتیجهٔ health/log و تست واقعی endpoint را ثبت کن. در چت جدید از کاربر تاریخچه را دوباره نخواه؛ همین سند را بخوان و از اولین اقدام باز ادامه بده.
5. پیگیری فرعی mobApp backend: آسیب‌پذیری‌های Trivy را رفع کن؛ scan را خاموش یا `--ignore-unfixed` را دور نزن. این کار مجوز Deploy به VPS نیست.
6. وضعیت نهایی PRها، SHAها، tag/digestهای Image و نتیجهٔ تست Production را در همین سند به‌روز کن.

## محدودیت عملیات

در این نقطه Workflowهای اعتبارسنجی Build اجرا شده‌اند، اما Workflowهای انتشار دستی اجرا نشده‌اند؛ هیچ Image جدیدی در GHCR publish نشده و هیچ سرویس/volume/VPS تغییر داده نشده است. PR #5 و PR #32 ادغام شده‌اند؛ PR #4، PR #31 و PR #8 هنوز باز هستند. هرگونه Publish یا Deployment به Production نیازمند تأیید صریح کاربر است.
