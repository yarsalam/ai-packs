# وضعیت اجرایی تجاری‌سازی YarSalam AI Packs

**آخرین بازبینی:** 2026-11-03  
**شاخهٔ مرجع:** `main`  
**SHA مرجع هنگام ثبت:** `66239f69b05909a176f071001f967ead46936d93`  
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

## ۲. ترتیب تجاری‌سازی

### مرحلهٔ ۱ — CI و اتوماسیون GitHub: تکمیل

- مسیرهای عمومی GHCR و GitHub Release در workflowهای پک‌ها غیرفعال‌اند.
- PR/manual workflowها build/validate می‌کنند؛ imageها محلی و artifactها موقت‌اند.
- regression test مربوط به release guardrails در CI اجرا می‌شود.
- validator benchmark دیگر اجازهٔ overwrite مسیر report موجود را نمی‌دهد.

### مرحلهٔ ۲ — مقایسهٔ UX بازار: تکمیل

تحقیق در `docs/COMPETITOR_UX_RESEARCH.md` محصولات Besedo/Implio، Hive و Sightengine را از نظر KPI، صف بررسی انسانی، دلایل flag، policy builder و thresholdها مقایسه می‌کند.

WordPress Preview و داشبورد Safety در PR #7 ادغام شده‌اند. KPIها، صف و داده‌های نمودار صرفاً synthetic demo هستند؛ به Gateway زنده متصل نیستند و نباید به‌عنوان نتیجهٔ مدل یا مشتری نمایش داده شوند.

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
- PHate و ParsHate در metadata فعلی GitHub مجوز صریح dataset ندارند.
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
