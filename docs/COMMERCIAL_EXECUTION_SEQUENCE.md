# ترتیب اجرای تجاری‌سازی AI Packs

**وضعیت به‌روزرسانی: 2026-11-03**

اصل تصمیم: مشتری‌یابی و فروش عمومی را جلوتر از اثبات کیفیت و آماده‌شدن محصول قرار ندهیم. مسیر کار دقیقاً به این ترتیب است.

## مرحله ۱ — حذف کار روزمرهٔ دستی از GitHub

**وضعیت: PR #10 برای بستن مسیرهای انتشار زودهنگام در حال CI؛ پس از merge این مرحله تکمیل می‌شود.**

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

**وضعیت: راهنمای annotation، مسیر جمع‌آوری امن، manifest و validator در PR وابسته به #10 آماده شده‌اند؛ corpus مجاز و اجرای واقعی باقی است.**

خروجی‌های آماده‌سازی:
- `docs/PERSIAN_SAFETY_ANNOTATION_GUIDE_FA.md` — taxonomy، actionها و adjudication.
- `docs/PERSIAN_SAFETY_DATA_COLLECTION_FA.md` — بررسی NASEZA/PHate/ParsHate و مسیر opt-in/قراردادی.
- `docs/templates/safety-benchmark-manifest.example.yaml` و `scripts/validate_safety_benchmark.py` — گیت حقوقی/حریم خصوصی، split، PII heuristic و aggregate-only validation.

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
