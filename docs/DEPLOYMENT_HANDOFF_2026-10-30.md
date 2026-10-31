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
- پس از run #4، commit `31989503311b4fab6867464d6ab432da76d87039` با یک تغییر کوچک، `RiskPanel` را صریحاً Client Component کرد؛ اجرای CI روی آخرین head هنوز باید تأیید شود.
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


## Production verification follow-up — 2026-10-31

A fresh read-only inspection of the live VPS supersedes the earlier assumption that the old pandas-broken ai_assistant image is still running.

Current live container:
- Container: `yarsalam-matching-pack-ai_assistant-1`
- Project/service: `yarsalam-matching-pack/ai_assistant`
- Image: `ghcr.io/yarsalam/ai-packs/matching-pack-ai-assistant:sha-b76cca762cb850ed8d75303e2613dce8e311dd7e`
- Image ID: `sha256:f54454ec2cba8c4b8ce9fc8525200c61cd40964095d082daa6000d4c1ece030d`
- Status: running, Docker health healthy
- Live checks inside container: `pandas==2.2.3`, `import app`, `from core.behavior import analyze_behavior` all pass.
- Internal `/health` endpoint returns HTTP 200 with Redis healthy.

**Decision:** Do not publish or redeploy ai_assistant. The live image already has the pandas correction. Do not touch any Matching services or SEO/Safety/Revenue Packs for the two-issue admin release. Keep the prior PR #4 merged history for traceability; it is not a reason to force another image rollout.

The remaining production work from the two original issues is Admin Web only:
- Existing admin container returns HTTP 200 from `/login`; this is route reachability only, not proof that a real admin login succeeds.
- Existing Compose dir: `/home/deploy/yarsalam-admin-prod-20261026`; existing Compose files are `docker-compose.yml,docker-compose.production.yml`.
- Current `NEXT_PUBLIC_API_URL` setting was `http://novertex.ir/api`. Plain HTTP redirects to HTTPS and the HTTPS certificate verifies.
- The actual login path `POST https://novertex.ir/api/admin/auth/login` was tested using a reserved fake `.invalid` identity: HTTP 401, zero redirects, valid TLS. This confirms the API route reached the backend; no real account was used.
- PR #33 in admin-panel was merged into `feat/production-deployment-memory` at `86245fa7a1a5e0cc2519da1e066499e5f977cafc`; it removes private `.env` injection from the web container. CI run `41182064502` passed.
- Admin Image is still not pushed and admin-web is still not replaced. Publish only the Admin image, then inspect the exact PLAN; do not deploy until separately authorized.


## Admin Proxy 502 recovery — 2026-10-31

- Admin Web public route was restored. The existing healthy Admin container was connected to the existing `yarsalam_network` with alias `admin-web`.
- Proxy-to-web reachability passed; Nginx config test and graceful reload passed; public `https://novertex.ir/login` now returns HTTP 200.
- No Admin or Proxy container was recreated/restarted; no image was pulled/built; no Matching service, volume or network outside the intended shared-network attachment was changed.
- Permanent Compose correction was merged in admin-panel PR #34 at `775ac7533179bf79302db26b4c8ce8b238fa2816` (tested head `3f2768cc703d11b536524026574ffc70bbc48432`). CI run `41188676377` passed. It adds the persistent external `yarsalam_network` and `admin-web` alias to the runtime Compose.
- The live Matching `ai_assistant` image remains healthy with pandas 2.2.3. No new Matching Image should be built or deployed.


## VPS Pack orchestration findings — 2026-10-31

Fresh read-only inspection of VPS 185.7.172.248 confirms the following runtime state:

- yarsalam-matching-pack: 7 running containers; ai_assistant, gateway, ml_service, personality, ai_support, and Redis are Healthy. model_init exited 0 as a one-shot initialization job. matching_embedded_ai is Healthy on the Matching project network only by design; it does not need a Backend-network alias because Matching's gateway consumes it internally.
- yarsalam-revenue-pack: all 6 containers are exited. Images remain present locally.
- yarsalam-seo-pack: all 7 containers are exited. Images remain present locally.
- yarsalam-safety-pack: no project/containers currently present on VPS.
- Main mobapp, admin panel/backend, and Matching containers were running at the time of inspection.

Docker inspect for Revenue and SEO recorded OOMKilled=false; application containers exited 143 and Redis exited 0. Docker journal recorded hasBeenManuallyStopped=true, daemonShuttingDown=false, and error=restart canceled. This is evidence of an intentional/manual stop path, not an OOM kill or ordinary app crash.

The deploy user's Bash history exposed the staged-pack orchestrator configuration:
- MIN_BEFORE_MB=4000
- MIN_AFTER_MB=1536
- order: seo-pack, revenue-pack, matching-pack, safety-pack
- the smoke-test helper checks gateway health and has explicit cleanup/stop paths.
- after the sequential test stage, the script has a separate section to leave SEO as the active pack.
- SEO stop branches include failed Compose startup/health wait, failed gateway probe, and available memory falling below 1536 MB.

Timing evidence from containers:
- Revenue started at 2026-10-30 14:37:42 UTC and stopped around 14:38:00 UTC (~18 seconds).
- SEO started at 2026-10-30 15:00:46 UTC and stopped around 15:52:09–15:52:11 UTC (~51 minutes).
- Event history query returned no container events; journal contains the stop evidence above.

Interpretation:
- The orchestrator intentionally tests packs sequentially under a conservative memory-headroom policy. Revenue's short runtime is consistent with a temporary smoke-test cycle; its subsequent stop is likely intentional cleanup, but the exact executed branch has not been proven from the visible history excerpt.
- SEO's stop is explicitly implemented in the orchestrator for failed startup/gateway health or low memory. The exact branch that ran at 15:52 UTC remains unconfirmed because the corresponding deployment log was not found.
- Do not remove or bypass the memory guards just to keep all Packs concurrently running. The host has 7.8 GiB RAM and Matching's embedding container alone was using roughly 770 MiB in the captured sample; actual inference peaks still need measurement.
- Do not rebuild/pull images or modify/restart healthy Matching, mobApp, or admin services during this diagnosis.
- The dashboard's 17-service probe has mismatched default hostnames/ports for some standalone pack services. ENOTFOUND is not evidence that those pack containers are absent; resolve health registry URLs to the actual Pack network aliases and internal ports. Keep embedded services internal where their gateways are the intended consumer.

Next operational decision:
1. Inspect the existing deployment log/previous orchestrator output if available, rather than generating more ad-hoc diagnostic scripts.
2. Decide the intended operating model: one active Pack at a time vs. a measured subset concurrently; do not promise all four simultaneously until memory/inference headroom is measured.
3. Restore/validate one Pack at a time using existing immutable GHCR images and its own Compose/env file; preserve volumes and other projects.
4. Correct the health dashboard registry separately from service deployment so it reports real endpoint availability rather than fallback DNS failures.


## Admin panel AI Pack controls — requested operating model (2026-10-31)

User requested an admin-panel control surface to stop AI Packs and test them one at a time while the product has no active users. This is a design requirement only; no runtime service was changed by this discussion.

### Resource evidence
- VPS RAM: 7.8 GiB total. At the last captured idle snapshot, MemAvailable was approximately 4.7 GiB; free-only memory was approximately 356 MiB, with the remainder largely reclaimable cache. Do not interpret low `free` alone as RAM exhaustion; use MemAvailable, cgroup memory, and peak measurements.
- Docker stats at that snapshot showed Matching's services consuming approximately 1.4 GiB combined, with matching_embedded_ai around 770 MiB. Whole-host MemAvailable was still about 4.7 GiB.
- Historical pack orchestration used MIN_BEFORE_MB=4000 and MIN_AFTER_MB=1536. These were conservative policy thresholds, not proof of OOM.
- Revenue containers were stopped after ~18s; SEO containers after ~51m. Docker journal says `hasBeenManuallyStopped=true`, `daemonShuttingDown=false`, `OOMKilled=false`. The exact executed stop branch remains unproven. SEO has explicit stop paths on failed startup/gateway test or MemAvailable below 1536 MiB. Do not claim that the host ran out of RAM without a matching memory sample.

### Preferred UI/operations model
- Add four Pack cards: SEO, Revenue, Matching, Safety. Safety is currently not installed on VPS; show NOT_INSTALLED rather than DOWN.
- Controls are pack-level, not arbitrary individual-container toggles: Start Test, Stop Pack, and pack-specific Test. Compose dependencies start in their declared order. Individual services are status-only in the first iteration.
- Add a prominent Stop All AI Packs action. It must target only fixed Compose projects yarsalam-seo-pack, yarsalam-revenue-pack, yarsalam-matching-pack, and yarsalam-safety-pack. It must never affect mobapp, admin, reverse proxy, MySQL, Redis, Qdrant or persistent volumes. Require explicit confirmation and audit the actor/action/result.
- Start/test is serialized by a host-side lock. Default to one new Pack at a time. A start operation records MemAvailable and cgroup memory before start, during warmup/model load, after health, and during functional gateway smoke tests. Use the existing 4000 MiB start / 1536 MiB reserve values as initial guardrails, configurable only through reviewed server-side policy. Abort or stop only the newly-started Pack if post-start reserve is breached; never auto-stop a previously healthy Pack.
- Run image-local health checks plus Pack gateway `/health` and small, non-destructive functional smoke tests. A green `/health` alone is not proof of functional quality.
- UI should distinguish STOPPED, STARTING, HEALTHY, DEGRADED, FAILED, NOT_INSTALLED, and UNKNOWN; include last action, timestamp, start/end RAM and test results.
- Make the current dashboard registry use actual Pack aliases/internal ports; do not show ENOTFOUND as an application failure when the backend is using a wrong default hostname/port. Keep embedded dependencies private to their Pack unless there is a specific backend API requirement.

### Security/implementation constraints
- Do not mount `/var/run/docker.sock` into admin web/backend containers. Docker socket access is effectively host-root and is not acceptable for a UI toggle.
- Implement a narrow host-side control agent/helper with a fixed allowlist of pack names, fixed Compose files/env paths, and only `start`, `stop`, `status`, and `test` operations. It must not accept arbitrary commands, paths, service names, or Docker arguments.
- The agent must serialize operations, use only each Pack's immutable image tags and current private env files, and run `docker compose stop` or controlled `up -d --pull never --wait`; never use `down -v`, `--remove-orphans`, volume prune, or system prune.
- Admin API requires a dedicated permission such as `manage_ai_packs`, strong authentication, CSRF-safe mutation handling, request validation, audit log, rate limit, and an explicit confirmation for Stop All.
- The host agent interface should be limited to a private Unix socket or similarly restricted local channel. Do not expose an unrestricted Docker API or privileged command runner to the web tier.
- Preserve current Architecture: GitHub stores source/tests/docs; VPS stores only runtime images, minimal Compose/config, private secrets, host control runtime and persistent data/model volumes.

### Suggested no-user validation sequence
1. Keep mobApp backend, admin stack, databases, proxy and their volumes running.
2. Use Stop All AI Packs only after verifying exact project allowlist; then verify Matching/SEO/Revenue are stopped and shared infrastructure remains healthy.
3. Start one Pack at a time using its existing local immutable images (`--pull never`), run gateway and functional smoke checks, record RAM peak/available reserve, then stop that Pack before moving to the next unless measured headroom and an explicit policy allow concurrent Packs.
4. Test Matching, SEO, Revenue; Safety remains NOT_INSTALLED until separately deployed and validated.
5. Only after measurements decide whether two or more Packs may remain active concurrently. Do not remove memory safeguards to make every dashboard dot green.

Implementation is not yet merged or installed. The next code change must be a coordinated, reviewed implementation across the host control agent, mobApp admin API, admin-panel UI, and tests/docs; do not add decorative or frontend-only toggles that cannot safely control real Pack state.


## Current admin pack-control implementation branch — 2026-10-31

Implementation is staged in `feat/admin-ai-pack-control-and-progressive-test` (PR pending at the time of this entry).
- Host agent: `scripts/ai_pack_control_agent.py`; installer: `scripts/install_ai_pack_control_agent.sh`.
- It exposes a fixed allowlist HTTP API only on the exact `yarsalam_network` bridge gateway IP; bearer token minimum 48 chars; operations serialized; audit report JSON saved under `/home/deploy/ai-pack-deploy-logs/control`.
- Start uses `--no-recreate --pull never --wait`; only existing immutable SHA images are accepted and no Pull/Build is possible. Stop uses Compose `stop` only. No `down`, orphan removal or volume commands exist.
- Progressive order: Matching, SEO, Revenue, Safety. Already-running Packs are not auto-stopped. A newly-started Pack is stopped only if startup fails or the memory safety reserve/emergency floor is crossed. Safety is skipped when not installed.
- Existing smoke test suite is reused, including SEO external URL audit + topical similarity, Revenue prediction + model-readiness metadata, Matching embedding + sentiment and Safety Persian moderation. SEO egress failure reports blocked outbound/VPN-dependent path without asserting VPN is the sole cause.
- Initial policy thresholds: MIN_START=2500 MiB, MIN_RESERVE=1536 MiB, emergency floor=1024 MiB. These are operational guardrails to be calibrated from actual peak RAM results, not evidence of an OOM event.
- Installer creates host systemd service and private token, updates only `AI_PACK_CONTROL_URL`/`AI_PACK_CONTROL_TOKEN` in the Admin private `.env` after backup, runs a single progressive test, and prints job JSON + final `free`/Docker stats. It does not deploy/restart Admin backend or web.
- Branch validation CI latest run `41204405691` for head `9a81d3d5559eaa6a0182e02d2b6fcee3a7aed781`: SUCCESS (Python compile, fixed allowlist/safe stop unit tests, installer shell syntax).
- The agent and install script are committed to GitHub only; no agent/systemd unit has yet been installed on the VPS. No live pack test or new RAM peak measurement has been performed by this assistant.

Admin-panel UI/API integration is being implemented separately in `yarsalam/admin-panel` branch `feat/admin-ai-pack-control-center`: superadmin-only controls, 4 Pack cards, per-pack Start/Stop/Test, Progressive Test, Stop All confirmation, live RAM and job polling. A separate backend-only runtime Compose and immutable GHCR publisher are needed because VPS must not build source. The Admin web and backend images must be published and deployed as runtime-only artifacts before the UI becomes visible on Production.

After review/merge and publishing: install the ai-packs host controller and execute the progressive tests once; then deploy only Admin backend and Admin web using their immutable runtime images. Do not change Matching, mobApp databases, Admin DB/Redis, Nginx or any volume except the explicitly allowlisted Pack Compose start/stop actions.


## Merge status update — 2026-10-31

- PR #6 `Add restricted Admin AI Pack controls and progressive RAM/function tests` is merged into `feat/safety-ghcr-deployment` at `cd7c2bda98d8ed5101832ce7d166f76863601334`.
- Final host-controller CI on its PR head `b4ca17dce1e98dcea59ac425a23282cb0cfdf4f3`: runs `41205008319`, `41205008485`, `41205008444` all SUCCESS; the controller-specific suite is run `41204405691` SUCCESS.
- The merge updated existing PR #2 checks and triggered validation-only builds: Safety and remaining Pack workflows publish only on manual `workflow_dispatch`, not on the current pull_request event. No registry publication was requested by this merge.
- The controller is still not installed on VPS, no live smoke tests or new RAM measurements have run. These require the operator-run bundle script after the Admin images are published.
- Exact merged ref for the VPS installer: `cd7c2bda98d8ed5101832ce7d166f76863601334`.