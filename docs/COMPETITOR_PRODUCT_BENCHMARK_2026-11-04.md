# بنچمارک رقابتی محصولات AI Packs — ۴ نوامبر ۲۰۲۶

**دامنه:** بررسی اسناد و صفحات عمومی رسمی رقبا برای SEO، Revenue و Matching؛ تحقیق UX مربوط به Safety در `docs/COMPETITOR_UX_RESEARCH.md` موجود است و در این سند به آن ارجاع می‌شود.

**روش و محدودیت:** این یک بررسی desk-research بر پایهٔ صفحات رسمی محصول/مستندات عمومی است، نه خرید حساب، تست عملی رقبا یا benchmark مدل. وجود قابلیت در صفحهٔ فروشنده به معنی اثبات کیفیت آن نیست. قیمت‌ها عمداً مقایسه نشده‌اند؛ باید از صفحهٔ قیمت رسمی و پلن/منطقهٔ دقیق در زمان خرید استخراج شوند.

## ۱. خلاصهٔ مدیریتی

| پک | محصولات مرجع برای مقایسه | انتظاراتی که بازار از محصول قابل‌فروش دارد | شکاف‌هایی که باید در کد/محصول خودمان راستی‌آزمایی شوند |
|---|---|---|---|
| SEO | Semrush AI Visibility، Profound، Peec AI، Ahrefs Brand Radar | پایش prompt و mention در چند answer engine، citation/source tracking، رقابت share-of-voice، تاریخچه و گزارش، توصیهٔ قابل اجرا | پوشش واقعی engineها، پایش زمان‌بندی‌شده، citation provenance، مقایسهٔ رقبا، دادهٔ تاریخی، خروجی قابل اقدام، API/export و پوشش فارسی |
| Revenue | AppsFlyer Measurement/Incrementality، RevenueCat Charts/LTV، Amplitude Experiment | اتصال eventها، cohort/LTV، attribution، آزمایش کنترل/variant، سنجش lift افزایشی و گزارش درآمد | صحت event schema، اتصال دادهٔ مشتری، cohortها، holdout/A-B، causal uplift، uncertainty/support، توضیح‌پذیری و اندازه‌گیری هزینه |
| Matching | Recombee، Algolia AI Recommendations، Bloomreach Discovery | توصیهٔ real-time، سیگنال تعامل، سناریو/قواعد، analytics، A/B testing و اندازه‌گیری conversion | چرخهٔ کامل event→recommendation→feedback، cold-start، فیلتر/قید، توضیح دلیل، diversity، A/B، معیارهای relevance و safety |
| Safety | Besedo/Implio، Hive Moderation Dashboard، Sightengine | hybrid automation/human review، policy و threshold per category، queue، appeal، audit و analytics | تحقیق UX اولیه در `docs/COMPETITOR_UX_RESEARCH.md` موجود است؛ benchmark واقعی فارسی و pilot همچنان به corpus مجاز نیاز دارد |

**نتیجهٔ مهم:** چهار پک فعلی را نمی‌توان صرفاً به‌خاطر وجود Gateway و میکروسرویس «رقیب‌پذیر» دانست. برای هر محصول باید مسیر دادهٔ ورودی، خروجی قابل‌فهم، اقدام بعدی، اندازه‌گیری نتیجه و تجربهٔ عملیاتی کامل شود. ادعاهای کیفیت یا ROI فقط با benchmark معتبر مجازند.

## ۲. SEO Pack

### محصولات مرجع

1. **Semrush AI Visibility** — https://www.semrush.com/solutions/ai-visibility/  
   صفحهٔ رسمی قابلیت benchmark کردن AI Visibility در برابر رقبا، مشاهدهٔ narrative/sentiment و یافتن موضوعاتی که رقبا در آن‌ها برتری دارند را توصیف می‌کند.
2. **Profound** — https://www.tryprofound.com/  
   مرجع مقایسه برای پایش حضور برند در پاسخ‌های AI، prompt intelligence و تحلیل citation/source؛ جزئیات هر قابلیت باید در بررسی مستقیم صفحهٔ جاری و پلن مربوط تأیید شود.
3. **Peec AI** — https://peec.ai/  
   مرجع تخصصی AI search visibility و پایش mention/competitor در answer engineها.
4. **Ahrefs Brand Radar** — https://ahrefs.com/brand-radar  
   مرجع مکمل برای brand mention و citation intelligence در کنار ابزارهای SEO سنتی.

### معیارهای UX/محصول

- انتخاب و مدیریت پروژه/دامنه و فهرست promptهای هدف با گروه‌بندی موضوعی.
- پوشش و نمایش صریح موتورهای پاسخ‌گو و تاریخ/زمان آخرین نمونه‌گیری؛ عدم نمایش دادهٔ stale به‌عنوان live.
- سهم mention/visibility در برابر رقبا، به تفکیک engine، prompt، topic و بازهٔ زمانی.
- نمایش پاسخ یا excerpt، citation URL و منبع قابل کلیک برای هر observation؛ حفظ provenance و زمان نمونه‌گیری.
- sentiment/narrative با برچسب «تحلیل مدل» و امکان اصلاح انسانی، نه score قطعی بدون توضیح.
- content/source gap: چه موضوع یا صفحه‌ای باعث می‌شود رقبا cited شوند و چه اقدام مشخصی باید انجام شود.
- گزارش مقایسه‌ای، export CSV/PDF و API؛ alert برای تغییر معنادار.
- فارسی و RTL، promptهای فارسی/انگلیسی، منطقه/زبان و variantهای نوشتاری.

### نگاشت اولیه به SEO Pack

ارزیابی فنی موجود در `docs/PRODUCT_AUDIT_2026-10-28.md` وجود مسیر محدود `POST /seo/audit/url` را برای چک‌لیست HTML (title، description، H1، canonical، lang، viewport، alt و links) ثبت کرده است. همان سند صریحاً می‌گوید این قابلیت crawler کامل یا امتیاز رتبه‌بندی Google نیست.

بنابراین این URL audit را نباید با یک پلتفرم AEO هم‌ردهٔ Semrush/Profound/Peec معرفی کرد. پیش از طراحی UI باید در کد منبع سرویس‌های `ai_seo`، `aeo_tracker`، `ai_backlink_quality` و `ai_seo_recommender` موارد زیر با تست و نمونهٔ خروجی بررسی شوند:

- آیا engineهای AI واقعاً query می‌شوند یا فقط connector/placeholder وجود دارد؟
- آیا prompt، پاسخ خام مجاز، citation URL، timestamp و model/engine version ذخیره می‌شوند؟
- آیا tracking تکرارشونده و تاریخچه وجود دارد یا صرفاً یک درخواست دستی است؟
- آیا backlink metrics از منبع دادهٔ واقعی می‌آیند و کیفیت لینک با معیار قابل بازتولید سنجیده می‌شود؟
- آیا recommendation به صفحه/بخش مشخص و اقدام فنی تبدیل می‌شود؟
- آیا rate limit، robots/ToS، SSRF/egress و provenance برای URL crawling کنترل شده‌اند؟

**حداقل Preview رقابتی:** صفحهٔ پروژه و promptها، AI visibility trend، competitor share، citation/source table، URL audit با evidence، فهرست actionهای اولویت‌بندی‌شده، export و نشانگر شفاف «Demo / no live data» در داده‌های نمایشی.

## ۳. Revenue Pack

### محصولات مرجع

1. **AppsFlyer Measurement Suite** — https://www.appsflyer.com/products/measurement/  
   صفحهٔ رسمی، attribution، cohort/marketing analytics و incrementality testing را در یک مجموعه معرفی می‌کند.
2. **AppsFlyer Incrementality** — https://www.appsflyer.com/products/measurement/incrementality/  
   مرجع مشخص برای آزمایش lift افزایشی و مقایسهٔ عملکرد کمپین‌ها با کنترل/آزمایش.
3. **RevenueCat Charts و LTV** — https://www.revenuecat.com/docs/dashboard-and-metrics/charts/realized-ltv-per-customer-chart  
   مرجع cohort-based realized LTV و تفکیک درآمد واقعی بر مبنای cohort.
4. **Amplitude Experiment** — https://www.amplitude.com/amplitude-experiment  
   مرجع طراحی آزمایش، segment analysis، data-quality checks و سنجش اثر تغییرات محصول.

### معیارهای UX/محصول

- اتصال و اعتبارسنجی event schema: user/customer pseudonymous ID، event، timestamp، amount، currency، channel/campaign و consent context.
- داشبورد cohort: retention، conversion، ARPU/ARPPU، realized/predicted LTV با تفکیک واضح actual در برابر forecast.
- تفکیک attribution همبستگی‌محور از incrementality علّی؛ last-touch attribution به‌تنهایی اثبات اثر کمپین نیست.
- تعریف آزمایش با hypothesis، control/holdout، variants، allocation، مدت، primary metric و guardrail metrics.
- گزارش lift با confidence interval/support count و بررسی sample-ratio mismatch، novelty و data quality.
- تفکیک revenue واقعی، forecast و scenario؛ ثبت فرض‌ها و نسخهٔ مدل.
- پیشنهاد اقدام با قابلیت ردیابی به داده و آزمایش؛ audit trail برای تغییر بودجه/کمپین.
- هزینهٔ پردازش و درآمد افزایشی در یک گزارش؛ عدم ادعای ROI بدون کنترل مناسب.

### نگاشت اولیه به Revenue Pack

کاتالوگ مخزن سرویس‌های `ai_monetization`، `ai_revenue`، `ai_uplift` و `ai_feedback` را فهرست می‌کند؛ اما نام سرویس به‌تنهایی اثبات‌کنندهٔ قابلیت محصول نیست. در ممیزی کد باید روشن شود:

- آیا ورودی eventهای واقعی با schema versioned وجود دارد؟
- LTV بر اساس cohort واقعی محاسبه می‌شود یا تخمین مدل بدون calibration است؟
- uplift از experiment/holdout و طراحی علّی به دست می‌آید یا صرفاً پیش‌بینی/همبستگی است؟
- baseline، sample count، uncertainty و leakage checks گزارش می‌شوند؟
- بازخورد به پیشنهاد/تصمیم وصل است و نتیجهٔ پس از اقدام اندازه‌گیری می‌شود؟
- آیا دادهٔ درآمد، ارز، refund، chargeback و timezone به‌درستی مدیریت می‌شود؟

**حداقل Preview رقابتی:** event health/import demo، cohort explorer، LTV actual-vs-predicted، experiment setup و lift report با دادهٔ synthetic، campaign comparison و recommendation log. هر مقدار synthetic باید به‌وضوح Demo باشد.

## ۴. Matching Pack

### محصولات مرجع

1. **Recombee** — https://www.recombee.com/features  
   مستندات رسمی، real-time recommendations، segmentation، semantic search، custom insights و scenario settings را شرح می‌دهند. راهنمای A/B: https://docs.recombee.com/ab-testing
2. **Algolia AI Recommendations** — https://www.algolia.com/products/ai-recommendations  
   ingestion کاتالوگ و interaction events، مدل‌های ML، real-time API، analytics و A/B testing را توصیف می‌کند.
3. **Bloomreach Discovery Recommendations** — https://documentation.bloomreach.com/discovery/docs/recommendations  
   پیکربندی widget و recommendation از داشبورد و override از طریق API را توضیح می‌دهد؛ مستند A/B: https://documentation.bloomreach.com/discovery/docs/ab-testing

### معیارهای UX/محصول

- پنل catalog/profile و وضعیت داده: تعداد entityها، ویژگی‌های ناقص، freshness و event ingestion errors.
- تعاملات user-item به‌عنوان سیگنال اصلی: impression، view، like/dislike، click، match، conversion و feedback؛ attribution با recommendation ID.
- scenario builder: هدف و محل نمایش، candidate filters، hard constraints، boosters و ranking strategy.
- real-time recommendation API با دلیل قابل‌فهم، scoreهای کالیبره‌نشده با برچسب مناسب و fallback روشن.
- cold-start برای کاربر/مورد جدید، diversity، novelty و جلوگیری از تکرار.
- A/B test با control، variant، traffic split و معیارهای offline/online.
- تحلیل relevance و business metrics: Recall@K/NDCG@K در offline و CTR/conversion/retention در online؛ این معیارها جای یکدیگر را نمی‌گیرند.
- کنترل fairness، safety و حریم خصوصی؛ فیلترهای hard constraint باید قبل از ranking اعمال شوند.

### نگاشت اولیه به Matching Pack

کاتالوگ مخزن سرویس‌های `ml_service`، `embedded_ai`، `personality`، `ai_assistant` و `ai_support` را ذکر می‌کند؛ این فهرست به‌تنهایی نشان نمی‌دهد که محصول یک recommender کامل با feedback loop و A/B testing دارد. ممیزی باید بررسی کند:

- آیا endpoint واقعاً top-K recommendation بر اساس user/item و context می‌دهد یا فقط embedding/similarity؟
- آیا eventها با `recommendation_id` به impression/click/match وصل می‌شوند؟
- آیا فیلترهای سن/ترجیحات/محدودیت‌های مجاز و safety قبل از ranking enforce می‌شوند؟
- آیا توضیح دلیل پیشنهاد، confidence calibration، diversity و cold-start وجود دارد؟
- آیا سنجش offline و آنلاین، baseline ساده و A/B test قابل اجراست؟
- آیا پروفایل و ویژگی‌های حساس حداقل‌سازی و دسترسی tenant-scoped دارند؟

**حداقل Preview رقابتی:** profile/catalog explorer با synthetic records، تنظیم scenario و فیلترها، کارت recommendation با دلیل، بازخورد like/dislike، توضیح cold-start، analytics و A/B test simulator. در محصول همسریابی، هرگز اطلاعات حساس واقعی را در Preview عمومی قرار ندهید.

## ۵. Safety Pack — مرجع موجود

مقایسهٔ Besedo/Implio، Hive و Sightengine و نیازمندی‌های operator overview، human review، policy builder و analytics در `docs/COMPETITOR_UX_RESEARCH.md` ثبت شده است. این تحقیق UX، benchmark کیفیت فارسی نیست. Issue #8 همچنان تا corpus مجاز، sealed test، privacy/legal review، load/cost و GO مستند BLOCKED است؛ Issue #9 وابسته و متوقف می‌ماند.

## ۶. الگوی مشترک برای ارتقای Dashboard و WordPress

برای هر پک، سه سطح UI جدا بسازید:

1. **Product Preview عمومی:** قابلیت‌ها، API examples، workflow و دادهٔ Demo برچسب‌خورده؛ بدون telemetry خصوصی یا endpoint عملیاتی.
2. **Customer workspace:** tenant/project، API keys با نمایش یک‌باره، usage، quota، invoices/plan state، API logs با redaction، integration status و docs.
3. **Operator/admin console:** وضعیت CI/release، نسخهٔ pack/model، health واقعی dependencyها، queue/errors، latency/cost و کنترل دسترسی؛ telemetry فقط از اتصال private read-only.

الزامات مشترک:
- RTL/Persian و English، responsive و accessibility.
- empty/loading/error/stale states؛ هیچ مقدار صفر/ساختگی به‌جای دادهٔ مفقود نمایش داده نشود.
- role-based access، audit trail، export و فیلتر زمانی.
- هر metric باید منبع، تعریف، timestamp و وضعیت واقعی/Demo داشته باشد.
- Preview عمومی نباید هیچ‌گاه به Gateway زنده، دادهٔ مشتری یا کنترل‌عامل خصوصی وصل شود.

## ۷. برنامهٔ اجرایی پیشنهادی برای سه پک باقی‌مانده

### گام A — ممیزی کد و API (قبل از طراحی)
برای هر سرویس، endpointها، schema، dependency، مدل/وزن، منبع داده، خطاها، تست‌ها و وضعیت واقعی inference را ثبت کنید. ادعای محصول از README به‌عنوان قابلیت اثبات‌شده پذیرفته نشود.

### گام B — Gap register و اولویت‌بندی
هر gap را با یکی از برچسب‌های `P0 security/data loss`، `P1 product blocker`، `P2 competitive UX`، `P3 polish` ثبت کنید. ابتدا P0/P1؛ سپس قابلیت‌هایی که یک workflow کامل کاربر را می‌سازند.

### گام C — Preview مستقل
برای هر پک یک preview offline و synthetic بسازید؛ هر demo interaction فقط در local state انجام شود. WordPress باید نصب/حذف، RTL، عدم فراخوانی شبکه در حالت preview، ZIP و compatibility را تست کند.

### گام D — تست و پذیرش
- unit/API contract/regression tests.
- integration با mock و dependency failure.
- cold install از ZIP در محیط پاک و مستقل.
- full inference واقعی با مدل‌های دارای مجوز و revision ثابت.
- security/privacy review، SBOM و license inventory.
- load/latency/error/cost با workload مشخص.
- UI smoke و accessibility.
- release gate مستقل برای هر پک؛ سبز شدن یک پک، مجوز انتشار پک دیگر نیست.

### ترتیب پیشنهادی اجرا
1. SEO: تکمیل رقابت AEO و URL audit به workflow قابل‌اقدام؛ سپس Preview و تست.
2. Revenue: ابتدا event/cohort و تعریف دقیق uplift؛ سپس Preview و تست.
3. Matching: ابتدا recommender و feedback loop واقعی؛ سپس Preview و تست.
4. Safety: آماده‌سازی governance کامل است؛ اجرای pilot فقط پس از حل blocker قانونی داده در Issue #8.

این ترتیب، اولویت پیشنهادی مهندسی است نه ادعای اینکه SEO/Revenue/Matching آماده‌تر یا سودآورترند. بعد از ممیزی کد ممکن است جابه‌جا شود.

## ۸. تصمیم‌های فروش و انتشار

- همهٔ پک‌ها فعلاً Technical Preview هستند؛ public release/GHCR و VPS deployment تا عبور گیت‌های مستقل مجاز نیست.
- هیچ benchmark، accuracy، uplift، revenue increase یا ROI بدون دادهٔ قانونی و ارزیابی بازتولیدپذیر ادعا نمی‌شود.
- فروش Safety و outreach در Issue #9 تا GO مستند Issue #8 متوقف است.
- فروش SEO/Revenue/Matching نیز تا تکمیل مجوز مدل/داده، کیفیت inference، امنیت، privacy/retention، cold install، load، latency/cost و release gates انجام نمی‌شود.
- هیچ دادهٔ production یارسلام برای demo یا benchmark export نمی‌شود؛ نسخهٔ تجاری مستقل باقی می‌ماند.

## منابع رسمی بررسی‌شده

- Semrush AI Visibility: https://www.semrush.com/solutions/ai-visibility/
- Profound: https://www.tryprofound.com/
- Peec AI: https://peec.ai/
- Ahrefs Brand Radar: https://ahrefs.com/brand-radar
- AppsFlyer Measurement: https://www.appsflyer.com/products/measurement/
- AppsFlyer Incrementality: https://www.appsflyer.com/products/measurement/incrementality/
- RevenueCat Realized LTV: https://www.revenuecat.com/docs/dashboard-and-metrics/charts/realized-ltv-per-customer-chart
- Amplitude Experiment: https://www.amplitude.com/amplitude-experiment
- Recombee Features: https://www.recombee.com/features
- Recombee A/B Testing: https://docs.recombee.com/ab-testing
- Algolia AI Recommendations: https://www.algolia.com/products/ai-recommendations
- Bloomreach Recommendations: https://documentation.bloomreach.com/discovery/docs/recommendations
- Bloomreach A/B Testing: https://documentation.bloomreach.com/discovery/docs/ab-testing
- Hive Moderation Dashboard: https://docs.thehive.ai/docs/what-is-the-moderation-dashboard
- Sightengine: https://sightengine.com/
- Besedo/Implio: https://besedo.com/
