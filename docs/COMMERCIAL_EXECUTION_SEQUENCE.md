# ترتیب اجرای تجاری‌سازی AI Packs

**وضعیت به‌روزرسانی: 2026-11-03**

اصل تصمیم: مشتری‌یابی و فروش عمومی را جلوتر از اثبات کیفیت و آماده‌شدن محصول قرار ندهیم. مسیر کار دقیقاً به این ترتیب است.

## مرحله ۱ — حذف کار روزمرهٔ دستی از GitHub

**وضعیت: تکمیل شد؛ PR #10 (غیرفعال‌سازی publish عمومی) و PR #12 (جلوگیری از overwrite گزارش خصوصی) با merge commit واقعی ادغام شدند؛ CI هر دو PR برابر ۸/۸ و CI آخرین main برابر ۵/۵ سبز است.**

- بررسی PR، CI، branch drift و وابستگی workflowها.
- اصلاح شکست‌ها و افزودن تست regression.
- merge PRهای کم‌خطر فقط پس از بررسی diff و سبز شدن همهٔ CIهای مرتبط.
- self-approval جعلی ممنوع است؛ اگر branch protection تأیید مستقل بخواهد، blocker صریح ثبت می‌شود.
- PR CI فقط build/validate دارد؛ publish و VPS deploy مسیرهای جداگانه‌اند.
- گزارش وضعیت در GitHub ثبت می‌شود؛ گزارش روزانهٔ تکراری به مالک ارسال نمی‌شود.

## مرحله ۲ — شناخت بازار و بازطراحی محصول

**وضعیت: تحقیق UX و Preview در PR #7 ادغام شده‌اند (2026-11-03).**

مراجع بررسی‌شده:
- Besedo/Implio: KPIهای moderation، سهم تصمیم خودکار/دستی، روند زمانی و صف دستی.
- Hive: review feed، دلیل پرچم‌گذاری، کارتابل محتوا/کاربر، policy، appeal و نقش اپراتورها.
- Sightengine: workflow builder، actionهای دسته‌ای و thresholdهای مستقل.

خروجی در مخزن:
- `docs/COMPETITOR_UX_RESEARCH.md`
- WordPress Preview با سه نمای Safety: overview، review queue و policy builder.
- مرکز کنترل فقط‌خواندنی WordPress برای CI و وضعیت محصولات؛ telemetry خصوصی فقط با اتصال سروری مجاز خوانده می‌شود.

تمام KPIها و محتواهای داشبورد عمومی فعلاً دادهٔ ساختگی و برچسب‌خورده به‌عنوان Demo هستند؛ این‌ها آمار واقعی مدل یا مشتری نیستند.

## مرحله ۳ — تبدیل Preview به پایلوت اندازه‌پذیر

**وضعیت: ابزارها و مسیر حاکمیت داده در PR #11 ادغام شده‌اند؛ validator در PR #12 نیز در برابر overwrite فایل موجود harden شده است. corpus مجاز/دارای رضایت هنوز وجود ندارد؛ بنابراین benchmark و پایلوت واقعی متوقف و issue #8 همچنان BLOCKED است.**

خروجی‌های آماده‌سازی:
- `docs/PERSIAN_SAFETY_ANNOTATION_GUIDE_FA.md` — taxonomy، actionها و adjudication.
- `docs/PERSIAN_SAFETY_DATA_COLLECTION_FA.md` — بررسی NASEZA/PHate/ParsHate و مسیر opt-in/قراردادی.
- `docs/templates/safety-benchmark-manifest.example.yaml` و `scripts/validate_safety_benchmark.py` — گیت حقوقی/حریم خصوصی، split، PII heuristic و aggregate-only validation.
- PR #12: مسیر خروجی گزارش aggregate اگر از قبل وجود داشته باشد رد می‌شود تا فایل خصوصی/گزارش قبلی overwrite نشود؛ ۳۱ تست Safety در check مربوطه موفق شد.

گیت‌های لازم:
1. مجموعهٔ دادهٔ فارسی با مجوز استفاده و حذف شناسه‌های مستقیم؛ متن خصوصی کاربران نباید به مخزن عمومی ارسال شود. هیچ candidate فعلی برای استفادهٔ تجاری تأیید نشده است.
2. راهنمای annotation برای spam، off-platform contact، harassment/abuse، threats و clean content؛ نمونه‌های رسمی، محاوره، Finglish، typo و code-switching.
3. دو annotator برای بخشی از داده و ثبت توافق/اختلاف.
4. جداسازی train/tune، validation و sealed test؛ دادهٔ sealed برای تنظیم threshold استفاده نشود.
5. اجرای `scripts/evaluate_moderation.py` روی endpoint آزمایشی و ذخیرهٔ report تجمیعی.
6. اجرای cold install و inference واقعی، load test، latency p50/p95، error rate و هزینهٔ هر ۱۰۰۰ درخواست.
7. بررسی model/dependency licenses، log/cache retention و data-processing terms.

**پیش از شروع هر پایلوت** معیار موفقیت و حدود قابل‌قبول false-positive/false-negative، latency و هزینه با design partner تعیین شود. عدد ثابت و عمومی برای همهٔ مشتری‌ها فرض نشود.

خروجی پایلوت:
- baseline مشتری قبل از AI؛
- نتایج مدل روی sealed test؛
- تعداد موارد خودکار، ارجاع و برگشت از تصمیم؛
- کار اپراتوری صرفه‌جویی‌شده و هزینهٔ واقعی؛
- فهرست شکست‌ها و تصمیم go/no-go.

## مرحله ۴ — جذب design partner و سپس مشتری پولی

**وضعیت: BLOCKED تا GO مستند issue #8؛ issue #9 عمداً متوقف است و هیچ outreach/proposal کیفیت/ROI انجام نمی‌شود.**

- ابتدا ۳ تا ۵ design partner در حوزهٔ شبکه اجتماعی، همسریابی، مارکت‌پلیس یا انجمن‌های فارسی.
- به‌جای فروش عمومی، دامنهٔ محدود، مدت، حجم، مسیر داده و معیار ROI پایلوت مشخص شود.
- فقط قابلیت‌هایی در proposal بیان شود که در benchmark/pilot واقعی مشاهده شده‌اند.
- پس از موفقیت پایلوت، offer تجاری، SLA، هزینه inference، پشتیبانی، پرداخت، تمدید و لغو License نهایی شود.

## همگام‌سازی با اپ یارسلام

نسخهٔ تجاری و production یارسلام مستقل می‌مانند. هر قابلیت اثبات‌شده باید:
1. قرارداد API و تست backward-compatible داشته باشد؛
2. در PR جداگانه به `mobApp` منتقل شود؛
3. روی staging و با دادهٔ ناشناس و مجاز تست شود؛
4. پس از انتشار مستقل و قابل بازگشت به اپ اصلی اضافه شود.

هیچ تغییر تجاری یا تست benchmark نباید به‌طور مستقیم منطق moderation، Redis یا دادهٔ کاربران زنده را تغییر دهد.


---

## وضعیت به‌روز — 2026-11-04

- استراتژی کامل قابلیت‌ها و معیارهای پذیرش چهار پک در `docs/COMMERCIAL_PRODUCT_STRATEGY.md` مرجع اصلی اجراست.
- Preview آفلاین هر چهار محصول در PR #21 وارد main شده است: Safety review/policy، SEO prompt/citation/technical audit، Revenue cohort/LTV/experiment و Matching Top-K/explanation/constraints/event funnel. تمام اعداد و داده‌ها synthetic هستند؛ این Previewها محصول زنده یا evidence کیفیت نیستند.
- تحقیق رسمی رقبا در `docs/COMPETITOR_PRODUCT_BENCHMARK_2026-11-04.md` ثبت شده و گپ‌ها به acceptance criteria تبدیل شده‌اند.
- Source pin و smoke/domain corrections در PR #24 با merge commit `0fe44582c4b9a673482319d4f11fb13d66dd6747` ادغام شده‌اند؛ ref توزیع فعلی mobApp برابر `4344cb05afe461551e1bfdc379b26a3c0fedddd9` است.
- Usage/quota dashboard چهار WordPress plugin و انتخاب engine در SEO در PR #26 در حال بررسی CI است؛ این پنل billing/payment نیست و وزن creditها provisional هستند.
- اولویت ادامه: (1) P0 نصب مستقل، security، tenant/privacy، model/dependency licensing؛ (2) SEO prompt/citation/history و safe crawler؛ (3) Revenue event/cohort/refund/experiment integrity؛ (4) Matching hard filters/scenario/feedback attribution؛ (5) Safety workflow polish بدون عبور از corpus gate.
- هر پک باید release gate مستقل را بگذراند. full inference، cold install، security/SBOM/licensing، privacy/retention/deletion، load/latency/error/cost هنوز GO نشده‌اند.
- Safety #8 تا corpus فارسی مجاز/رضایت‌مند، annotation/adjudication و sealed benchmark BLOCKED می‌ماند؛ #9 و outreach متوقف است.
- هیچ GHCR/public Release، فروش، outreach، production deployment یا تغییر سرویس زنده مجاز نیست.


### وضعیت اجرایی جدید — 2026-11-05
- PR #26 exact-head checks روی `aeb0d69f599384badd540c49631aa5e97cf8e92b`: چهار workflow توزیع، Gateway contract، Safety image و سایر image validation همگی success؛ PR همچنان Draft و نیازمند review کامل diff است.
- PR #27 exact-head checks روی `621b6ef9297b4ed0bc45936e201056660f90bf3b`: چهار workflow success. این PR pin چهار workflow را از mobApp PR #6 head `9474b4ace1da44d6c2662b0554918ae521c7eaec` جلو می‌برد؛ تا merge/reconcile شدن upstream PR #6 نباید merge شود.
- mobApp PR #11 و #12 latest-head Python readiness موفق‌اند؛ هر دو هنوز Draft و stacked بر PR #6 هستند.
- mobApp PR #15 یک fail-closed remediation برای Revenue LTV provenance/missingness اضافه کرده و منتظر exact-head CI است؛ Issue #13 همچنان باز و ادعاهای LTV تجاری ممنوع است.
