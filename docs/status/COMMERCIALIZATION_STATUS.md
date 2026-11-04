# وضعیت اجرایی تجاری‌سازی YarSalam AI Packs

**آخرین بازبینی:** 2026-11-04  
**شاخهٔ مرجع:** `main`  
**SHA مرجع هنگام ثبت:** `63f9d2ce88f0972f40e357b20feeeedeb14dc658`  
**تصمیم انتشار عمومی:** **NO-GO**

این سند وضعیت GitHub و شواهد موجود را ثبت می‌کند؛ سبز بودن CI یا ساخته‌شدن image/ZIP به معنی تأیید کیفیت مدل یا مجوز عرضه نیست.

## ۱. وضعیت GitHub و CI

| PR | موضوع | نتیجه | Merge commit | شواهد CI |
|---|---|---|---|---|
| [#7](https://github.com/yarsalam/ai-packs/pull/7) | Safety Preview، داشبورد WordPress و تحقیق UX | merged | `e04263027c00e64c6bed0b34488a670530557977` | ۹/۹ checks موفق روی head PR |
| [#10](https://github.com/yarsalam/ai-packs/pull/10) | غیرفعال‌سازی GHCR و GitHub Release عمومی | merged | `63200213961e176f58fd643f40a38219d4d08b45` | ۸/۸ checks موفق |
| [#11](https://github.com/yarsalam/ai-packs/pull/11) | راهنمای annotation، مسیر دادهٔ خصوصی و validator | merged | `0d617dfa136e437f92e05087208b37785e5de44c` | ۸/۸ checks موفق؛ ۳۰ تست Safety در مجموعهٔ اختصاصی |
| [#12](https://github.com/yarsalam/ai-packs/pull/12) | جلوگیری از overwrite گزارش/فایل خصوصی موجود | merged | `66239f69b05909a176f071001f967ead46936d93` | ۸/۸ checks موفق؛ ۳۱ تست Safety |

- CI پس از merge شدن PR #12 روی main: run `41663587208`، هر ۵ check موفق.
- این سند از طریق PR مستنداتی #13 ارائه شده است؛ snapshot اولیه پس از ادغام PRهای قبلی و پیش از بازشدن PR #13 تهیه شد.
- PRهای #10، #11 و #12 با merge commit واقعی ادغام شدند؛ هیچ force update انجام نشد.
- metadata شاخهٔ `main` در GitHub مقدار `protected=false` و `protection.enabled=false` را گزارش می‌کند و API مربوط به repository rulesets فهرست خالی برگرداند؛ بنابراین در زمان بررسی، الزام review مستقل/approval فعال نبود. endpoint جزئیات protection برای این اتصال 403 داد. هیچ self-approval یا review جعلی ثبت نشد.

### سخت‌سازی شاخه‌های قدیمی و مسیرهای دستی انتشار — 2026-11-03

ممیزی همهٔ شاخه‌ها نشان داد چند شاخهٔ تاریخی هنوز نسخهٔ قدیمی workflowهای `workflow_dispatch` را داشتند که `packages: write`، ورود به GHCR و `docker push/--push` یا trigger انتشار GitHub Release را نگه داشته بود؛ خاموش‌کردن publish فقط روی `main` برای بستن این مسیر کافی نبود.

برای بستن مسیرهای قدیمی، بدون force update و با commitهای واقعی دووالدی/merge، workflowهای امن `main` به این شاخه‌ها منتقل شدند:
- `feat/safety-ghcr-deployment`: `43d1a5ec08441865b4b2196e23fc4511da141946`
- `feat/ai-products-wordpress-preview`: `3f80c17c660ff5b32301a2fc4224500d4f5aa66d`
- `feat/safety-dashboard-product-preview`: `654df3d92a72dedfd417d85fc4db251671789240`
- `feat/admin-ai-pack-control-and-progressive-test`: `82b61c56bdb8ddc6147c8e7fbbf91b8ffeb81ca1` و سپس `c800ef746a38b5050d6a13b96efa37ac6ba395c0`
- `fix/matching-ai-assistant-runtime-image`: `b77d611530472266412ccb9bbfd97a5528f1de80` و سپس `50b41fc9c2597059f59889c2290eb4d2bfc645d7`
- `fix/pack-live-smoke-followups-2026-10-29`: `9e87dd79aa1df15d078255d1bf9d63e71c7433f9`
- `fix/commercial-readiness-baseline`: `310cff3d002caa5b3e17040fdd79c52525a76c93`

پس از به‌روزرسانی، workflowهای شاخه‌های بالا دوباره بررسی شدند: هیچ `packages: write`، `docker/login-action`، `docker push/--push` یا trigger/asset upload برای GitHub Release باقی نمانده است. فقط artifact موقت CI با retention محدود مجاز است. شاخه‌های ثبت‌کنندهٔ قدیمی نیز به شاخه‌های امن‌شده اشاره می‌کنند. هیچ GHCR publish، GitHub Release یا VPS deployment اجرا نشد.

## ۲. ترتیب تجاری‌سازی

### مرحلهٔ ۱ — CI و اتوماسیون GitHub: تکمیل

- مسیرهای عمومی GHCR و GitHub Release در workflowهای پک‌ها غیرفعال‌اند.
- PR/manual workflowها build/validate می‌کنند؛ imageها محلی و artifactها موقت‌اند.
- regression test مربوط به release guardrails در CI اجرا می‌شود.
- validator benchmark دیگر اجازهٔ overwrite مسیر report موجود را نمی‌دهد.

### مرحلهٔ ۲ — مقایسهٔ UX بازار: تحقیق هر چهار پک ثبت شد؛ اجرای Previewهای بعدی در جریان

- Safety: تحقیق Besedo/Implio، Hive و Sightengine در `docs/COMPETITOR_UX_RESEARCH.md` و WordPress Preview/داشبورد در PR #7 ادغام شده‌اند.
- SEO، Revenue و Matching: تحقیق رقابتی در `docs/COMPETITOR_PRODUCT_BENCHMARK_2026-11-04.md` با PR #15 و merge commit `63f9d2ce88f0972f40e357b20feeeedeb14dc658` وارد main شد. منابع رسمی شامل Semrush/Profound/Peec/Ahrefs، AppsFlyer/RevenueCat/Amplitude و Recombee/Algolia/Bloomreach هستند.
- PR #15 فقط مستندات بود؛ diff یک فایل جدید با ۲۰۲ خط بود، `mergeable=true` و `mergeable_state=clean` داشت، و API هیچ workflow/check-run مرتبطی برای SHA آن گزارش نکرد. بنابراین این merge به‌معنی عبور CI مدل یا کیفیت inference نیست.
- PR #14 به‌علت branch drift با PR #15 جایگزین و بدون merge بسته شد؛ شاخهٔ جایگزین مستقیماً از main ساخته شد، بدون force update.

WordPress Preview فعلی فقط Safety را به‌صورت تعاملی نشان می‌دهد. KPIها، صف و داده‌های نمودار synthetic demo هستند؛ به Gateway زنده متصل نیستند و نباید به‌عنوان نتیجهٔ مدل یا مشتری نمایش داده شوند. Preview سه پک دیگر هنوز باید ساخته شود.

### مرحلهٔ ۳ — Safety pilot اندازه‌پذیر: ابزار آماده، داده مسدود

موارد آماده:
- راهنمای فارسی taxonomy، action و adjudication در `docs/PERSIAN_SAFETY_ANNOTATION_GUIDE_FA.md`.
- مسیر opt-in/قراردادی، provenance، privacy و retention در `docs/PERSIAN_SAFETY_DATA_COLLECTION_FA.md`.
- manifest خصوصی pending و validator aggregate-only در `docs/templates/safety-benchmark-manifest.example.yaml` و `scripts/validate_safety_benchmark.py`.
- تست‌های validator برای مجوز تجاری، privacy fields، PII heuristic، duplicate، source-group leakage، sealed split و جلوگیری از overwrite.
- تست CI روی خروجی standalone برای semantic outage در single و batch؛ نتیجه باید fail-closed و review باشد.

**مانع واقعی فعلی:** هیچ corpus فارسی برای استفادهٔ تجاری این پایلوت تأیید نشده است.

بررسی metadata مخازن عمومی:
- NASEZA مجوز CC0-1.0 دارد، اما داده از گفتگوهای Telegram گردآوری شده و مبنای privacy/consent و حقوق اشخاص ثالث برای این محصول روشن نیست؛ فقط candidate برای بررسی حقوقی است.
- PHate در GitHub metadata مجوز ندارد؛ ParsHate نیز `license=null` دارد و README فعلی آن را صریحاً «for research only» معرفی می‌کند؛ برای commercial benchmark پذیرفته نیست.
- ParsCN یک candidate جدید ۱٬۱۰۰ جفتی با ادعای CC BY 4.0 در README است، اما metadata مخزن/Zenodo مجوز dataset را ثبت نکرده و ۴۵۰ نمونه از PHATE و بقیه از منابع upstream/LLM مشتق شده‌اند؛ chain-of-rights، privacy/consent و مجوز منابع پایه روشن نیست. فقط برای بررسی حقوقی باقی می‌ماند.
- هیچ‌کدام به‌تنهایی taxonomy و توزیع موردنیاز محصول dating/social فارسی را کامل پوشش نمی‌دهند.

پس هیچ‌کدام وارد benchmark یا sealed test نشده‌اند. راه امن باقی‌مانده: مجوز کتبی و provenance/privacy روشن از صاحب حق، یا دادهٔ opt-in از شریک/پنل داوطلبان با رضایت قابل‌پس‌گرفتن و retention/deletion مشخص. دادهٔ production یارسلام نباید استفاده یا export شود.

### مرحلهٔ ۴ — design partners و مشتری پولی: مسدود

Issue [#9](https://github.com/yarsalam/ai-packs/issues/9) تا ثبت GO مستند در [#8](https://github.com/yarsalam/ai-packs/issues/8) متوقف است. هیچ outreach، proposal کیفیت، ادعای ROI یا فروش شروع نشده است.

## ۳. وضعیت گیت‌های عرضه

| گیت | وضعیت |
|---|---|
| مجوز مدل‌ها، وزن‌ها و dependencyها | OPEN |
| corpus فارسی قانونی و de-identified | BLOCKED — هیچ corpus تأییدشده |
| annotation دوگانه و adjudication واقعی | NOT STARTED |
| sealed test و benchmark واقعی | NOT RUN |
| امنیت، SBOM و dependency scan | OPEN |
| privacy، log/cache/retention و deletion review | OPEN |
| cold install و inference کامل از cache خالی | NOT COMPLETE |
| load، latency، error rate و هزینهٔ هر ۱۰۰۰ درخواست | NOT MEASURED |
| صف واقعی review، audit، appeal و incident operations | PREVIEW ONLY |
| مجوز release عمومی، GHCR یا VPS | NOT AUTHORIZED |

## ۴. مرزهای عملیاتی

- نسخهٔ تجاری AI Packs مستقل از اپ و سرویس عملیاتی یارسلام باقی می‌ماند.
- هیچ تغییر production، deployment، stop/restart سرویس، تغییر secret، Redis/DB/volume، DNS، firewall یا migration در این مسیر انجام نشده است.
- هر قابلیت اثبات‌شده برای اپ داخلی فقط با PR جداگانه، قرارداد backward-compatible و آزمون staging قابل بررسی است.
- تا عبور همهٔ release gates و GO مالک در issue #8، public publish و VPS deployment ممنوع باقی می‌ماند.

## ۵. اقدام بعدی

1. تهیهٔ corpus با مجوز/رضایت معتبر و ثبت provenance/privacy در فضای خصوصی.
2. تکمیل de-identification و بازبینی انسانی PII؛ سپس annotation دوگانه و adjudication.
3. ساخت splitهای source-group و sealed test با دسترسی محدود.
4. اجرای baseline و sealed evaluation روی محیط مستقل؛ ثبت support، confusion matrix، precision/recall/F1، FPR/FNR و latency.
5. تکمیل licensing، security، privacy/retention، cold install، load و cost gates.
6. فقط پس از شواهد کامل، تصمیم GO/NO-GO در issue #8؛ سپس بازکردن مرحلهٔ #9.


## ۶. به‌روزرسانی اجرایی — 2026-11-04

### PR و تحقیق بازار
- PR [#15](https://github.com/yarsalam/ai-packs/pull/15) با merge commit واقعی `63f9d2ce88f0972f40e357b20feeeedeb14dc658` ادغام شد؛ تنها یک سند تحقیقاتی اضافه شد. هیچ کد اجرایی تغییر نکرد.
- PR [#14](https://github.com/yarsalam/ai-packs/pull/14) به‌عنوان branch قدیمی superseded بسته شد و merge نشد.
- Issue [#16](https://github.com/yarsalam/ai-packs/issues/16) برای ممیزی کد SEO، Revenue و Matching، ثبت gapها، Previewها و گیت‌های تست ایجاد شد.

### ممیزی اولیهٔ source در مخزن mobApp
این یافته‌ها از کد عمومی `yarsalam/mobApp` به دست آمده‌اند و هنوز نیازمند بررسی کامل tests، workflowها و inference هستند:
- **SEO:** AEO tracker در کد بررسی‌شده فقط provider مربوط به OpenAI را اجرا می‌کند؛ mention با substring ساده محاسبه می‌شود و خطای provider به‌صورت `mentioned=false` گزارش می‌شود. Backlink TrustFlow فعلی PageRank روی edgeهای ورودی caller است، نه crawler/index مستقل. پیشنهادهای SEO شامل expected ROI/revenue ثابت و hard-coded هستند و نباید به‌عنوان نتیجهٔ اندازه‌گیری‌شده نمایش داده شوند.
- **Revenue:** LTV از featureهای دستی با defaultهای ثابت تغذیه می‌شود؛ مقدار `confidence` در predictor همان CV R² است، نه احتمال کالیبره، و بازهٔ ±۱۵٪ ثابت prediction interval آماری نیست. Uplift در نبود econml به اختلاف میانگین treated/control fallback می‌کند؛ این fallback به‌تنهایی causal uplift معتبر نیست. CORS wildcard در monetization نیز نیازمند بازبینی امنیتی است.
- **Matching:** ranking فعلی از cosine similarity و revenue signal استفاده می‌کند؛ engagement فعلاً ثابت ۰٫۵ و revenue fallback ثابت ۰٫۳۵ است. cold-start می‌تواند به شناسه‌های پیش‌فرض ۱ تا ۵۰ با score ثابت ۰٫۸۵ برسد و match score در نبود embedding مقدار ثابت ۰٫۴۵ برمی‌گرداند. event stream وجود دارد، اما feedback loop کامل و attribution recommendation-to-outcome هنوز اثبات نشده است. Assistant دادهٔ bio/messages/events را در Redis و فایل JSON ذخیره می‌کند؛ retention/deletion و tenant isolation باید ممیزی شوند.
- جزئیات و اولویت‌ها در comment مربوط به Issue #16 ثبت شده‌اند. هیچ‌یک از این یافته‌ها مجوز تغییر production نیست.

### اتوماسیون روزانه
- Automation «پیشبرد خودکار ai-packs» فعال است و prompt آن برای پوشش تحقیق رقابتی، source audit، Preview، تست‌ها و release gates به‌روزرسانی شد.
- آخرین اجرای ثبت‌شده در 2026-11-03 با وضعیت `failed` تمام شده و پیام نتیجه «There was a problem with your scheduled task» است؛ `next_run_time` نیز در وضعیت فعلی null است.
- بنابراین تا زمان مشاهدهٔ یک اجرای زمان‌بندی‌شدهٔ موفق، اجرای پیوستهٔ روزانه تأییدشده محسوب نمی‌شود. درخواست اجرای فوری در همین نوبت پذیرفته شد و کار آن در همین گفتگو ادامه یافت.

**تصمیم فعلی:** public release همچنان NO-GO. هیچ GHCR publish، VPS deployment، production change، secret access، service stop/restart یا data/volume mutation انجام نشده است. Issue #8 و #9 طبق شروط قبلی مستقل و مسدود باقی می‌مانند.
