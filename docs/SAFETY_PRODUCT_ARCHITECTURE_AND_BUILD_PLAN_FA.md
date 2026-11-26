# معماری هدف و برنامهٔ ساخت Safety Pack
**تاریخ:** ۲۶ نوامبر ۲۰۲۶  
**وضعیت:** طرح اجرایی پیشنهادی؛ نه معماری production آماده و نه مجوز انتشار.

## ۱. تصمیم محصول

Safety Pack را به‌عنوان سامانهٔ عملیاتی Trust & Safety برای پلتفرم‌های فارسی‌زبان می‌سازیم، نه API سادهٔ تشخیص توهین.

### دامنهٔ اولیه
- محتوای متنی فارسی در پست، کامنت و پیام؛
- اسپم و تبلیغ ناخواسته؛
- انتقال مکالمه به خارج از پلتفرم و دورزدن قواعد تماس؛
- آزار و تهدید متنی؛
- صف بررسی انسانی، سابقهٔ تصمیم و اعتراض.

### خارج از MVP
- تشخیص چهره و احراز هویت بیومتریک؛
- تحلیل ویدئو و صوت؛
- ban دائمی خودکار؛
- ادعای تشخیص کلاهبردار، نیت یا شخصیت کاربر؛
- compliance certification و تضمین پوشش حقوقی کشورها.

قابلیت‌های تصویر و face verification موجود در مخزن باید از محصول اولیه جدا و به‌عنوان ماژول‌های مستقل با ارزیابی حقوقی و حریم خصوصی جداگانه بررسی شوند. دادهٔ بیومتریک صرفاً به دلیل وجود endpoint وارد مسیر اصلی moderation نمی‌شود.

## ۲. اصول معماری

1. **Policy-first:** تصمیم نهایی از policy نسخه‌دار tenant و سیگنال‌های قابل توضیح پیروی کند؛ خروجی خام مدل معادل تخلف نیست.
2. **Human-in-the-loop:** موارد مبهم یا پرریسک به انسان ارجاع شوند؛ امکان override، appeal و reversal وجود داشته باشد.
3. **Fail-safe:** خرابی یا timeout مدل نباید به block خاموش و غیرقابل مشاهده منجر شود. مسیر جایگزین باید بر اساس policy به review یا defer برود.
4. **Tenant isolation:** هر رکورد، کلید، فایل، صف و گزارش باید tenant-scoped باشد و جداسازی با تست منفی اثبات شود.
5. **Privacy by default:** متن خام در logهای عملیاتی نوشته نشود؛ retention و deletion قابل اجرا و آزمون باشند.
6. **Provider/model agnostic:** اتصال مدل از طریق adapter و با ثبت نسخه، checksum و تنظیمات انجام شود.
7. **Auditable decisions:** هر تصمیم شامل actor، policy version، signals، زمان، دلیل و تغییرات بعدی باشد.
8. **No invented quality claims:** تا benchmark مستقل نداریم، precision/recall/accuracy تبلیغاتی منتشر نمی‌شود.

## ۳. معماری منطقی هدف

Customer App / Website
  → Public API / SDK / WordPress Connector
  → API Gateway: authentication، tenant resolution، rate limits، idempotency، validation
  → Ingestion + Normalization: Persian/Arabic normalization، ZWNJ، ارقام، Finglish، PII minimization
  → Policy & Decision Orchestrator
      → Rules Engine
      → Model Adapters
      → Context Signals
  → Decision: allow / review / restrict / defer
      → Human Review Queue
      → Customer Webhook
  → Case Management / Appeals / Audit
  → Analytics / QA / Usage Metering

### اجزای زیرساختی پیشنهادی

| لایه | انتخاب اولیه | ملاحظه |
|---|---|---|
| API | FastAPI، نسخه‌بندی /v1 | قرارداد OpenAPI، validation، request IDs |
| Control plane | سرویس مدیریت tenant، کاربران، نقش‌ها و کلیدها | جدا از مسیر inference |
| Database | PostgreSQL | منبع حقیقت برای tenant، policy، case، appeal و audit |
| Queue | Redis + worker در شروع؛ abstraction قابل تعویض | retry، dead-letter، idempotency |
| Cache / rate limit | Redis | محدودیت per-tenant و per-key |
| Object storage | S3-compatible در صورت نیاز | رمزنگاری، retention و lifecycle |
| Frontend | React/Next.js، TypeScript | کنسول واقعی، نه HTML نمایشی |
| Observability | structured logs، metrics، tracing | عدم ثبت متن خام در log |
| Delivery | Docker، CI، migrations، SBOM و image scan | build تکرارپذیر و بدون secret در image |

این‌ها انتخاب‌های پیشنهادی‌اند، نه ادعای وجود زیرساخت آماده. انتخاب نهایی باید با هزینهٔ میزبانی، توان عملیاتی و نیاز مشتری سازگار شود.

## ۴. مرز سرویس‌ها و مدل داده

### Control plane
- tenants
- tenant_members
- roles / permissions
- api_keys (فقط hash؛ نمایش secret فقط هنگام ساخت)
- policies / policy_versions
- plans / usage_entitlements
- integration_endpoints

### Moderation plane
- moderation_events
- content_references
- moderation_signals
- moderation_decisions
- review_cases
- case_assignments
- case_notes
- user_risk_events
- appeals
- audit_events
- webhook_deliveries

هر جدول tenant-owned باید tenant_id داشته باشد. دسترسی به شناسهٔ رکورد به‌تنهایی کافی نیست؛ queryها باید tenant scope را اعمال کنند و تست cross-tenant access وجود داشته باشد.

### قواعد نگهداری داده
- شناسهٔ محتوای مشتری را از متن خام جدا نگه داریم.
- متن خام فقط در صورت نیاز قراردادی و با retention مشخص نگهداری شود.
- حذف tenant باید شامل DB، object storage، cache، queue و backup lifecycle مستند باشد.
- دادهٔ مشتری برای آموزش مدل استفاده نشود مگر با اجازهٔ مستقل و صریح.
- محتوای شخصی و حساس وارد analytics یا log عمومی نشود.

## ۵. قرارداد API اولیه

- POST /v1/moderation/events — دریافت event با tenant از هویت معتبر، نه ورودی قابل جعل.
- GET /v1/moderation/events/{event_id} — وضعیت و نتیجه با tenant scoping.
- GET /v1/review/cases — صف بازبینی با فیلتر و pagination.
- GET /v1/review/cases/{case_id} — جزئیات پرونده و context مجاز.
- POST /v1/review/cases/{case_id}/decision — تصمیم بازبین.
- POST /v1/appeals — ثبت اعتراض.
- POST /v1/appeals/{appeal_id}/resolution — نتیجهٔ بازبینی اعتراض.
- GET /v1/policies و PUT /v1/policies/{policy_id} — مدیریت policy و نسخه.
- GET /v1/audit-events — تاریخچهٔ قابل ممیزی.
- POST /v1/webhooks/test — آزمون اتصال؛ webhook واقعی باید امضاشده و دارای retry باشد.

تمام APIها نیازمند schema، authentication، authorization، rate limit، idempotency و contract tests هستند. این فهرست قرارداد هدف است، نه endpointهای فعلی.

## ۶. مدل تصمیم‌گیری

خروجی استاندارد:
- allow
- review
- restrict، فقط در policy محدود و قابل برگشت
- defer، در اختلال فنی یا نبود context

هر تصمیم باید policy ID و version، model/provider/version در صورت استفاده، signals و categoryها، confidence خام همراه معنای تعریف‌شده، reason codes، override انسانی، latency و مسیر fallback را ثبت کند.

هیچ confidence منفردی نباید به‌عنوان احتمال قطعی تخلف نمایش داده شود. قواعد قطعی و مدل باید از هم قابل تشخیص باشند.

## ۷. امنیت و قابلیت اطمینان — معیار پذیرش

- tenant isolation با تست منفی برای API، DB access، queue، cache، object storage و analytics؛
- secret hashing/rotation و عدم افشای secret در پاسخ یا log؛
- webhook HMAC، timestamp، replay protection و retry محدود؛
- idempotency برای ingestion و تصمیم‌های تکرارشونده؛
- bounded payload size، timeout، concurrency و rate limits؛
- dependency pinning، SBOM، vulnerability scan و image provenance؛
- migrations قابل rollback و backup/restore test؛
- readiness/liveness جداگانه؛
- error budget و SLO پس از اندازه‌گیری بار واقعی؛
- عدم ذخیرهٔ متن خام در log؛ masking شناسه‌های شخصی؛
- threat model و privacy/data-flow review پیش از pilot.

## ۸. برنامهٔ ساخت مرحله‌ای

### مرحلهٔ ۰ — تثبیت پایه و حذف ابهام
- بررسی Gateway و سرویس‌های فعلی، dependencyها و قراردادهای واقعی؛
- تفکیک قابلیت‌های متن، تصویر و biometrics؛
- انتخاب یک use case و taxonomy؛
- تثبیت PR دمو/ممیزی و نگه‌داشتن release gateها؛
- threat model و data-flow map.

**خروجی:** architecture decision records، inventory و test baseline.

### مرحلهٔ ۱ — Control plane امن
- PostgreSQL و migrations؛
- tenant، user، role و API key؛
- authentication، authorization، rate limits و audit پایه؛
- tenant isolation tests؛
- secrets و config management.

**معیار پایان:** هیچ دسترسی cross-tenant در مجموعهٔ تست‌ها موفق نشود.

### مرحلهٔ ۲ — Ingestion و تصمیم قطعی
- event API نسخه‌دار؛
- Persian normalizer با تست‌های adversarial؛
- policy schema و deterministic rules؛
- queue، retry، DLQ و idempotency؛
- decision record و webhook امضاشده.

**معیار پایان:** مسیر end-to-end با مدل خاموش هم قابل اجرا، قابل ردیابی و fail-safe باشد.

### مرحلهٔ ۳ — کنسول اپراتور
- inbox، assignment و case detail؛
- approve/restrict/escalate/defer؛
- notes، audit و appeal؛
- RBAC و ثبت هویت actor؛
- UI با دادهٔ synthetic برای demo و API واقعی برای محیط داخلی.

**معیار پایان:** تمام تصمیم‌ها از UI به API ثبت شوند و audit کامل داشته باشند.

### مرحلهٔ ۴ — مدل و benchmark فارسی
- corpus مجاز و de-identified مخصوص taxonomy منتخب؛
- annotation guide و adjudication؛
- split بدون leakage بر اساس source/user/time؛
- sealed test و per-class metrics؛
- threshold calibration و abstention؛
- مدل و وابستگی‌های دارای مجوز روشن.

**معیار پایان:** معیارهای توافق‌شده با مشتری در دادهٔ مستقل پاس شوند؛ در غیر این صورت مدل فقط advisory بماند.

### مرحلهٔ ۵ — عملیات تجاری
- usage metering واقعی و قابل reconcile؛
- cost per 1,000 events؛
- load، p50/p95، error rate و resource profile؛
- billing، plan enforcement و tenant admin؛
- runbooks، incident response و support.

### مرحلهٔ ۶ — پایلوت محدود و انتشار
- قرارداد، DPA و محدودهٔ داده؛
- نصب سرد از artifact مستقل؛
- backup/restore و rollback؛
- security/privacy sign-off؛
- معیار پذیرش مکتوب و go/no-go مستقل.

## ۹. وب‌سایت شرکت و مسیر جذب سفارش

وب‌سایت شرکت مستقل از داشبورد محصول طراحی شود و دو هدف را پوشش دهد.

### پیام اصلی
«طراحی و توسعهٔ سامانه‌های نرم‌افزاری اختصاصی برای کسب‌وکارها؛ از API و پنل مدیریتی تا اتوماسیون و محصولات داده‌محور.»

### صفحات
1. Home — ارزش پیشنهادی، حوزه‌ها و CTA مشخص.
2. Services — توسعهٔ نرم‌افزار، backend/API، پنل، اتوماسیون، AI integration.
3. Work / Engineering demos — دموهای واقعی با برچسب prototype یا production.
4. Products — Safety Pack با وضعیت دقیق preview / pilot / available.
5. Engineering — معماری، امنیت، تست، deployment و روش تحویل.
6. About — مسئولیت‌ها و توانمندی واقعی، بدون رزومه و مشتری ساختگی.
7. Contact / Request a proposal — فرم brief پروژه و راه ارتباطی معتبر.

### کانال‌های جذب سفارش
- صفحات تخصصی برای هر خدمت و جست‌وجوی ارگانیک؛
- case study فنی از پروژه‌های واقعی یا نمونه‌های synthetic با برچسب demo؛
- ویدئوی کوتاه walkthrough از محصول و فرایند مهندسی؛
- همکاری white-label با آژانس‌های طراحی، بازاریابی و شرکت‌های IT؛
- پلتفرم‌های فریلنسری و بازارهای پروژه؛
- محتوای فنی هدفمند در LinkedIn و شبکه‌های مرتبط؛
- تبلیغات جست‌وجویی کوچک برای یک خدمت با landing page و سنجش lead؛
- پیشنهاد ارزیابی فنی یا نمونهٔ محدود پولی به‌جای مشاورهٔ نامحدود رایگان.

### فرایند فروش
Lead → qualification → discovery → scope & exclusions → paid discovery/prototype → proposal → contract → milestone delivery → handover/support.

هیچ لوگوی مشتری، testimonial، نتیجهٔ مالی یا سابقهٔ پروژه‌ای بدون مدرک منتشر نشود.

## ۱۰. معیارهای موفقیت و توقف

- زیرساخت امن و قابل نصب، نه صرفاً CI سبز؛
- demo با workflow واقعی و دادهٔ ساختگی شفاف؛
- یک vertical و taxonomy مشخص؛
- حداقل یک design partner پیش از تعهد به مقیاس بزرگ؛
- هزینه و کیفیت اندازه‌گیری‌شده؛
- امکان حذف داده و جداسازی tenant اثبات‌شده؛
- مسیر درآمد از خدمات توسعه، حتی اگر فروش محصول زمان ببرد.

اگر corpus مجاز، کیفیت قابل قبول یا willingness-to-pay پیدا نشد، دامنه را محدود یا محصول را متوقف می‌کنیم؛ اما اجزای عمومی مهندسی و قابلیت ارائهٔ خدمات توسعه همچنان قابل استفاده‌اند.

## ۱۱. مرز انتشار

این سند اجازهٔ merge، انتشار image، Release، استقرار production، ارسال پیشنهاد تجاری Safety یا استفاده از دادهٔ کاربران YarSalam را صادر نمی‌کند. وضعیت NO-GO در docs/RELEASE_GATES.md و موانع Issue #8 و #9 تا ارائهٔ شواهد لازم پابرجا هستند.
