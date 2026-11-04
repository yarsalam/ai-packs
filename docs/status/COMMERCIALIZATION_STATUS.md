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


## ۷. به‌روزرسانی اجرایی — 2026-11-04 (ادغام استراتژی و ممیزی source)

### PRها و CI
- PR [#19](https://github.com/yarsalam/ai-packs/pull/19) با merge commit واقعی `328f0688bc2140c03867e29e96de5ecf2033ceca` ادغام شد؛ سند `docs/COMMERCIAL_PRODUCT_STRATEGY.md` اکنون در main مرجع رسمی امکانات هدف و معیار پذیرش چهار پک است. run شماره 154 روی head آن موفق بود.
- PR [#18](https://github.com/yarsalam/ai-packs/pull/18) با merge commit واقعی `4c443e6ea6f55ae2be99958ff2c7132e61bf2f14` ادغام شد؛ رزرو quota در هر چهار Gateway با Redis Lua اتمیک است. 429 دیگر counter را افزایش نمی‌دهد. تست هم‌زمانی با Redis واقعی و چهار workflow مرتبط موفق شدند: Gateway contract matrix، Safety image validation، self-contained distributions و SEO/Revenue/Matching image validation. همه jobهای گزارش‌شده success بودند.
- SHA فعلی main هنگام ثبت این update: `4c443e6ea6f55ae2be99958ff2c7132e61bf2f14`.

### ممیزی کد و شکاف‌های محصول
- ممیزی منبع با سند `docs/COMMERCIAL_SOURCE_AUDIT_2026-11-04.md` ثبت شد؛ مرجع upstream بسته‌بندی `mobApp@49718c978cda59237b2c6a206bdbe301accda157` است.
- یافته‌های مهم SEO: فقط OpenAI provider در AEO؛ خطای engine به‌صورت mention=false برمی‌گردد؛ TrustFlow فعلی PageRank روی graph ورودی است نه شاخص backlink مستقل؛ خطای embedding در topic similarity به 0.0 تبدیل می‌شود؛ recommender در شرایطی popularity fallback دارد.
- یافته‌های مهم Revenue: CV R² به‌عنوان confidence استفاده شده و range ثابت ±۱۵٪ prediction interval معتبر نیست؛ uplift در نبود EconML به اختلاف میانگین treated/control fallback می‌کند؛ fallbackهای قدیمی باید از ref بسته‌بندی جداگانه بازبینی شوند.
- یافته‌های مهم Matching: engagement ثابت 0.5، revenue default برابر 0.35، cold-start با شناسه‌های ثابت و score ثابت 0.85 و match score fallback برابر 0.45؛ event route هنوز contract کامل attribution را اثبات نمی‌کند.
- یافتهٔ مشترک: فیلد domain در License ذخیره می‌شود اما در `validate_license` بررسی نمی‌شود؛ سیاست domain binding و billing شکست upstream باید تعریف و تست شوند.

### وابستگی upstream — BLOCKED برای تغییر pin
- workflow توزیع در `.github/workflows/distributions.yml` از ref ثابت `49718c978cda59237b2c6a206bdbe301accda157` استفاده می‌کند.
- `mobApp/main` در زمان بررسی روی `da4acf20c9851bc4e7fd34b1dcc2094183246109` بود؛ GitHub compare بین این دو تاریخچه را `diverged` با `ahead_by=1 / behind_by=24` گزارش کرد.
- commit جدید mobApp/main اصلاح مهم LTV (flat feature contract، URL داخلی و حذف fallback عدد ساختگی) دارد، اما چون تاریخچه‌ها diverged هستند، تغییر سادهٔ pin ممنوع است. ابتدا lineage و ۲۴ commit بررسی، سپس PR جدا و تمام build/contract tests اجرا شود.

### کارهای بعدی دقیق
1. بررسی lineage upstream و reconcile ref بدون force update؛ سپس re-run توزیع و API contracts.
2. اصلاح Revenue correctness و خروجی uncertainty/fallback در PR مستقل.
3. اصلاح Matching scoring/cold-start/hard filters و event attribution در PR مستقل.
4. اصلاح SEO AEO error-state/provenance و backlink naming/failure semantics.
5. تکمیل Previewهای آفلاین SEO، Revenue و Matching و تست‌های UI.
6. تکمیل release gates مستقل؛ فروش و public release همچنان NO-GO.

**محدودیت‌ها:** این مرحله فقط audit و تغییرات quota/مستندات را پوشش می‌دهد؛ full inference، حقوق مدل/داده، privacy، cold install، load، p95 latency، error rate و cost-per-1000 هنوز برای هر پک GO نشده‌اند. Safety #8 همچنان BLOCKED و #9 متوقف است.


## ۸. به‌روزرسانی اجرایی — 2026-11-04 (Preview و License Domain Binding)

### WordPress Preview چهار محصول
- PR [#21](https://github.com/yarsalam/ai-packs/pull/21) با merge commit واقعی `2488e6ad37869047078e208320f61beaf716d47e` ادغام شد.
- Preview آفلاین WordPress اکنون برای هر چهار محصول پنل دارد: Safety (نمای کلی/صف/policy)، SEO (prompt/citation/technical audit)، Revenue (actual/cohort/LTV/experiment) و Matching (Top-K/explanation/constraints/event funnel).
- برای پنل‌های SEO/Revenue/Matching حالت‌های ready/loading/empty/error/stale قابل تغییر است. داده‌ها synthetic و بدون اتصال به Gateway/production هستند. connectorهای SEO که هنوز پیاده‌سازی نشده‌اند صریحاً «هنوز متصل نشده» نشان داده می‌شوند؛ اختلاف خام Revenue به‌عنوان causal uplift نمایش داده نمی‌شود.
- workflow `validate-and-package` موفق شد؛ پنج check دیگر Gateway/Matching نیز روی head PR موفق شدند. ZIP فقط artifact موقت CI است، Release عمومی ساخته نشده است.

### License domain binding — IN_PROGRESS
- PR [#22](https://github.com/yarsalam/ai-packs/pull/22) در branch `feat/license-domain-binding` با head SHA `dfcdf530628dd388618ae360dc2fa37d2ae6ac38` باز است؛ CI آن باید روی آخرین head دوباره بررسی شود.
- هر چهار Gateway اکنون در PR تغییر کرده‌اند تا domain مشخص در License با هدر `X-Site-Domain` مقایسه شود؛ domain wildcard `*` برای سازگاری قدیمی آزاد می‌ماند. mismatch پیش از quota metering رد می‌شود.
- هر چهار WordPress API client هدر دامنه را ارسال می‌کنند؛ Safety در مسیر JSON و multipart. Gateway هدر را پیش از proxy به upstream حذف می‌کند.
- تست‌های contract برای match/mismatch/missing/wildcard/normalization و رد قبل از meter اضافه شده‌اند؛ CI PHP syntax و وجود header در هر plugin نیز افزوده شده است.
- سند قرارداد `docs/LICENSE_DOMAIN_BINDING.md` محدودیت امنیتی را شفاف می‌کند: این کنترل فقط policy/anti-misconfiguration است، نه اثبات رمزنگاری‌شدهٔ مالکیت دامنه؛ bearer key قابل استفاده با header جعلی است.

### Upstream PRها
- mobApp PR #6 همچنان Draft است؛ `pack-regressions` سبز و mergeable/clean است، اما full inference/clean install/load باقی است. PR #7 نیز Draft و پیاده‌سازی URL audit همپوشان دارد؛ ادغام هر دو بدون reconcile ممنوع.
- distribution pin روی SHA PR #6 باقی است تا lineage و قراردادها با تاریخچهٔ فعلی mobApp reconcile شوند.

**وضعیت کلی:** PR #21 Preview را به سطح چهار محصول گسترش داد، اما این فقط UI demo است. Release gates و full inference برای هر پک هنوز NO-GO هستند. Safety #8 BLOCKED و #9 متوقف است.


## ۹. به‌روزرسانی اجرایی — 2026-11-04 (Domain Binding و Source Reconciliation)

### License domain binding — DONE IN PR #22
- PR #22 با merge commit واقعی `bce27e145b7be3c6a6a27337e507004cedf9772b` ادغام شد.
- هر چهار Gateway دامنهٔ مشخص License را با `X-Site-Domain` مقایسه می‌کنند؛ mismatch/missing قبل از quota metering رد می‌شود؛ `domain="*"` برای سازگاری قدیمی باقی است.
- هر چهار WordPress API client هدر را ارسال می‌کنند؛ Safety در JSON و multipart؛ Gateway هدر را به upstream forward نمی‌کند.
- contract tests، PHP syntax و header checks و image validation موفق شدند. قرارداد و محدودیت امنیتی در `docs/LICENSE_DOMAIN_BINDING.md` است. این فقط policy/anti-misconfiguration است، نه اثبات رمزنگاری‌شدهٔ مالکیت دامنه.

### Upstream source pin — IN_PROGRESS
- mobApp PR #10 با merge commit واقعی `d7ad4c17eb98caa3d5674a619753407e4ccb01ab` current main را به branch `fix/ai-pack-commercial-readiness` ادغام کرد؛ PR #6 اکنون تاریخچهٔ main و readiness را بدون force-push حفظ می‌کند.
- آخرین mobApp PR #6 head برابر `e017905c39835c1da2ddb3e8fd5f6bcd4c8e745b` است؛ PR هنوز Draft و merge نشده.
- regression workflow روی این SHA: **28 passed, 4 warnings**؛ Revenue LTV contract: **8 passed**.
- AEO provider failure اکنون `unavailable` است، نه negative mention؛ failed calls cache نمی‌شوند و از denominator حذف می‌شوند.
- Matching fallbackهای ثابت و IDهای ساختگی حذف شده‌اند؛ cold-start فقط از popularity مشاهده‌شده در candidate set استفاده می‌کند؛ missing embeddings امتیاز جعلی نمی‌دهند.
- LTV CV scaler داخل foldها fit می‌شود؛ CV R² با confidence اشتباه نمی‌شود؛ interval ثابت حذف و uncalibrated علامت می‌خورد. Uplift fallback فقط descriptive است و هیچ causal claim نمی‌کند.
- AI Packs source pin در branch `build/pin-mobapp-readiness-2026-11-04-final` به SHA بالا تغییر داده شده و PR #24 باز است؛ CI توزیع/تصویر/قرارداد روی آخرین head در حال اجراست. تا سبز شدن همهٔ checks، pin جدید در main فعال نیست. PR قبلی #23 به دلیل پایهٔ قدیمی و نبود client changes لازم بسته شد؛ merge نشده.

### گپ‌های باقی‌مانده
- Feature store در mobApp هنوز برای چند ورودی LTV از default/hard-coded values استفاده می‌کند؛ دادهٔ واقعی/provenance و cohort/temporal validation لازم است.
- Full inference واقعی، cold install، load/latency/error/cost per 1000 و حقوق مدل/وزن‌ها هنوز برای همهٔ پک‌ها اثبات نشده‌اند.
- English localization و customer workspace واقعی (نه Preview) هنوز باقی است.
- Safety corpus/benchmark هنوز BLOCKED در Issue #8؛ Issue #9 و فروش/outreach Safety ممنوع.
- همهٔ پک‌ها هنوز NO-GO برای فروش/public release تا عبور مستقل release gates و GO مالک.


### Safety WordPress JSON header follow-up — FIX IN PR #24
- Post-merge path review found that PR #22 had added `X-Site-Domain` to Safety multipart uploads but missed its separate JSON request method. Therefore, domain-bound Safety text moderation and license-status calls could still receive 403.
- PR #24 adds the header to Safety JSON requests and strengthens CI to require at least two occurrences in Safety API client (JSON + multipart). Until PR #24 merges, Safety WordPress domain binding is not fully complete.
- The live smoke-test client was also updated to send `X-Site-Domain` on license validation, inference and usage calls; degraded-but-reachable health is a warning, not a hard failure.


### Smoke-test contract — PR #24
- `scripts/smoke_test_packs.py` اکنون `X-Site-Domain: smoke-test.local` را در license validation، inference و usage ارسال می‌کند تا با domain binding هماهنگ باشد.
- health=degraded ولی reachable به‌صورت WARN ثبت می‌شود و smoke test مسیرهای مستقل را ادامه می‌دهد.
- Matching smoke test جدید بررسی می‌کند recommendationها فقط از candidate allowlist باشند و نبود embedding در `/match/predict` به HTTP 503 صریح منجر شود، نه score ساختگی.
- unit/static contract این موارد در PR #24 اضافه شده؛ اجرای live smoke روی محیط disposable هنوز انجام نشده و release gate آن باز است.


### Upstream AEO multi-engine revision — 2026-11-04
- mobApp PR #6 latest tested head: `4344cb05afe461551e1bfdc379b26a3c0fedddd9`.
- OpenAI + Perplexity Sonar adapters; all configured engines run by default; explicit selection supported; per-engine rates are separate; no cross-engine average; citations/model provenance retained; missing/unconfigured provider is `unavailable`, never a negative mention.
- Exact-head validation: **33 passed, 17 warnings** in Python AI readiness; **8 passed** in Revenue LTV contract.
- AI Packs PR #24 now pins all four distribution/CI/image-validation workflows to this SHA and passes Perplexity env configuration into SEO service; final AI Packs checks still required.
- Live Perplexity call remains BLOCKED pending an owner-provided test API key; no live provider success is claimed. PR #6 remains Draft; full inference/clean install/load/cost gates remain open.
