# استراتژی تکمیل محصول و نقشهٔ اجرای رقابتی AI Packs

**تاریخ ثبت:** 2026-11-04  
**مخزن:** `yarsalam/ai-packs`  
**وضعیت کل:** Technical Preview — هنوز آمادهٔ فروش یا انتشار عمومی نیست  
**مرجع بازار:** `docs/COMPETITOR_PRODUCT_BENCHMARK_2026-11-04.md` و `docs/COMPETITOR_UX_RESEARCH.md`  
**مرجع ممیزی:** Issue [#16](https://github.com/yarsalam/ai-packs/issues/16)  
**تصمیم انتشار:** NO-GO تا عبور مستقل هر پک از Release Gates

این سند «فهرست دقیق محصولی که باید ساخته شود» و دفتر راهنمای ادامهٔ کار اتوماسیون است. وجود قابلیت در این سند به معنی پیاده‌سازی‌شدن آن نیست. هر مورد فقط پس از وجود کد، تست و شواهد قابل بازتولید از ستون باز به انجام‌شده منتقل می‌شود.

## 1. اصول تصمیم‌گیری محصول

1. محصول باید یک مسئلهٔ تجاری کامل را از ورودی تا نتیجه و اقدام بعدی حل کند؛ مجموعه‌ای از endpointهای پراکنده یا صرفاً یک مدل ML محصول قابل فروش نیست.
2. قابلیت‌های رقبا از اسناد و صفحات رسمی عمومی استخراج شده‌اند؛ این تحقیق desk research است، نه تست عملی حساب رقبا و نه اثبات کیفیت آن‌ها.
3. مزیت رقابتی باید با benchmark و دادهٔ قانونی اثبات شود. هیچ ادعای accuracy، uplift، ROI، رتبهٔ گوگل یا کاهش تقلب بدون شواهد مجاز نیست.
4. ابتدا P0 امنیت/یکپارچگی داده، سپس P1 قابلیت اصلی محصول و workflow کامل، بعد P2 قابلیت رقابتی و P3 polish اجرا شود.
5. هر پک release gate مستقل دارد. سبز شدن CI یا آماده‌شدن Preview به معنی اجازهٔ فروش نیست.
6. Preview عمومی فقط offline و synthetic است؛ به Gateway زنده، production یارسلام یا دادهٔ مشتری متصل نمی‌شود.
7. انتشار GHCR، GitHub Release عمومی، فروش، outreach و deployment تا GOهای مجاز ممنوع است. Safety تابع شروط سخت‌گیرانهٔ Issue #8 و #9 می‌ماند.

## 2. امکانات مشترک لازم برای هر چهار محصول

| اولویت | قابلیت | معیار پذیرش |
|---|---|---|
| P0 | نصب مستقل و self-contained | ZIP/Compose هر پک بدون checkout مخزن خصوصی mobApp و بدون build context بیرون از بسته نصب شود؛ cold install از محیط پاک ثبت شود |
| P0 | امنیت License و Tenant | کلید فقط در header، tenant-scoped، revoke فوری، expiry/plan enforcement سمت سرور، عدم افشای secret، تست cross-tenant |
| P0 | کنترل مصرف و هزینه | quota اتمیک، رد درخواست بدون مصرف credit، usage قابل حسابرسی، limitهای plan و محافظت در برابر درخواست هم‌زمان |
| P0 | سلامت و خطا | تفکیک liveness/readiness، dependency health واقعی، timeout/retry policy محدود، error envelope نسخه‌بندی‌شده و fail-closed در نقاط حساس |
| P0 | امنیت زنجیرهٔ تأمین | SBOM هر artifact، pin نسخه و checksum مدل، dependency/image scan، license inventory و بررسی حق redistribution |
| P0 | حریم خصوصی | data-flow map، حداقل‌سازی PII، redaction، retention قابل تنظیم، deletion قابل راستی‌آزمایی، audit بدون ذخیرهٔ محتوای حساس غیرضروری |
| P1 | API contract و مستندات | OpenAPI کامل، auth/error/rate-limit examples، curl و quickstart؛ تست contract در CI |
| P1 | نصب و تجربهٔ مشتری | راهنمای نصب هدف کمتر از ۱۰ دقیقه، `.env.example` امن، upgrade/rollback و troubleshooting |
| P1 | Customer workspace | پروژه/tenant، وضعیت License، کلیدها با نمایش یک‌باره، usage/quota، نسخهٔ پک، وضعیت integration و لینک مستندات |
| P1 | عملیات و مشاهده‌پذیری | structured logs با redaction، request ID، latency/error/throughput، model/pack revision، export و audit trail |
| P1 | SDK و integration | SDK حداقل Python، TypeScript و PHP یا مثال‌های رسمی معادل؛ webhook signature/retry/idempotency در جایی که webhook وجود دارد |
| P2 | نقش‌ها و گردش کار تیمی | RBAC، دعوت کاربر، نقش operator/admin، تغییرات قابل ممیزی و مدیریت دسترسی |
| P2 | مدیریت اشتراک و پرداخت | تعریف plan/entitlement، مصرف واقعی، فاکتور/پرداخت/تمدید/لغو و پورتال مشتری؛ فقط پس از اندازه‌گیری هزینه و انتخاب provider، نه با قیمت‌های حدسی |
| P2 | پشتیبانی تجاری | changelog، status/incident runbook، نسخه‌بندی و پشتیبانی/تعهدات متناسب با پلن |
| P3 | تجربهٔ بصری نهایی | accessibility، responsive، ترجمهٔ کامل فارسی/انگلیسی، empty/loading/error/stale و polish |

**Preview مشترک:** برای هر پک یک Product Preview عمومی و یک Operator/Admin Preview جدا؛ هر دو Demo واضح، دادهٔ ساختگی و بدون درخواست شبکه به سرویس عملیاتی. telemetry خصوصی فقط از اتصال private و read-only مجاز است.

## 3. SEO Pack — از URL audit به پلتفرم SEO و AI Search قابل اقدام

**نمونه‌های بازار:** Semrush AI Visibility، Profound، Peec AI، Ahrefs Brand Radar و Semrush SEO API.  
**کار اصلی خریدار:** بفهمد برند/محتوا در جست‌وجوی سنتی و پاسخ‌های AI چگونه دیده می‌شود، رقبا کجا جلوترند و دقیقاً چه اصلاحی باید انجام دهد.

| اولویت | قابلیت مورد انتظار | معیار پذیرش |
|---|---|---|
| P0 | URL fetch امن و SSRF-resistant | allow/deny شبکه، کنترل DNS و redirect، منع IP خصوصی/metadata، محدودیت حجم/زمان/MIME و تست DNS rebinding |
| P0 | provenance داده | هر observation دارای منبع، engine، زمان نمونه‌گیری، زبان/منطقه، revision و وضعیت stale باشد |
| P1 | مدیریت پروژه و دامنه | چند پروژه، دامنه، نقش، locale، رقبا و تنظیمات crawl |
| P1 | AI visibility / prompt tracking | prompt library با topic/tag، اجرای زمان‌بندی‌شده و تاریخچه برای engineهای واقعاً متصل؛ engine پشتیبانی‌نشده یا خطا هرگز به صورت «عدم mention» گزارش نشود |
| P1 | چندموتوره و locale | connectorهای واقعی و تست‌شده برای answer engineها؛ نمایش دقیق پوشش، محدودیت و آخرین اجرای هر engine؛ فارسی/انگلیسی و RTL |
| P1 | Mention و share of voice | محاسبهٔ قابل بازتولید در برابر competitorها با denominator/support count و تفکیک engine/topic/time |
| P1 | Citation/source intelligence | پاسخ/excerpt مجاز، citation URL قابل کلیک، دامنهٔ منبع، زمان و provenance؛ حذف/تغییر منبع در تاریخچه قابل پیگیری باشد |
| P1 | Technical SEO audit | crawl محدود و امن چندصفحه‌ای، title/meta/H1/canonical/robots/sitemap/schema/links/alt/performance signals؛ هر یافته با URL و evidence |
| P1 | Actionable recommendations | مشکل، صفحهٔ هدف، evidence، اولویت، گام اصلاح و وضعیت اجرا؛ هیچ expected revenue/ROI ثابت یا ساختگی |
| P2 | Content/source gap | موضوع و منبعی که رقبا در آن cited می‌شوند، فرصت محتوایی و ارتباط با صفحهٔ موجود |
| P2 | Sentiment/narrative analysis | تحلیل با برچسب مدل، شواهد متنی، confidence غیرکالیبره با هشدار و امکان بازبینی انسانی |
| P2 | Alert و گزارش | alert تغییر مهم visibility/citation، گزارش زمان‌بندی‌شده، CSV/PDF و API |
| P2 | Backlink intelligence | منبع دادهٔ backlink واقعی، provenance، معیارهای شفاف کیفیت/spam و تاریخچه؛ PageRank روی ورودی محدود caller به‌عنوان TrustFlow یا crawler معرفی نشود |
| P3 | Workflow تیم محتوا | assignment، status، notes، export و integrationهای CMS |

**Preview SEO:** پروژه/دامنه، prompt manager، trend و competitor share، جدول citation، URL audit evidence، action backlog، فیلتر engine/topic/date، export demo و هشدار دادهٔ synthetic/stale.

**موانع/راستی‌آزمایی‌های باز:** پوشش واقعی AEO providerها؛ تاریخچه و scheduler؛ منبع backlink؛ crawler امن؛ پیشنهادهای hard-coded؛ کیفیت/پوشش فارسی. موارد فعلی فقط پس از ممیزی endpoint/schema/source/test به‌عنوان implemented علامت بخورند.

## 4. Revenue Pack — از پیش‌بینی منفرد به چرخهٔ اندازه‌گیری و رشد درآمد

**نمونه‌های بازار:** AppsFlyer Measurement/Incrementality، RevenueCat Charts/LTV و Amplitude Experiment.  
**کار اصلی خریدار:** بفهمد درآمد از کجا می‌آید، کدام cohort ارزشمند است و کدام اقدام واقعاً درآمد افزایشی ایجاد کرده است.

| اولویت | قابلیت مورد انتظار | معیار پذیرش |
|---|---|---|
| P0 | event ingestion contract | schema نسخه‌بندی‌شده، pseudonymous customer ID، event ID، timestamp/timezone، amount/currency، campaign/channel و consent context؛ validation و idempotency |
| P0 | tenant/data isolation | جداسازی tenant، کنترل دسترسی، redaction، retention/deletion و جلوگیری از نشت بین مشتریان |
| P1 | event health/import | ingest API و import امن CSV، خطاهای schema، duplicate، late/out-of-order events و پوشش داده |
| P1 | cohort analytics | cohort explorer برای acquisition/activation/retention/conversion، ARPU/ARPPU و realized LTV بر اساس درآمد واقعی |
| P1 | Actual vs forecast | برچسب روشن actual/predicted/scenario، model/version، assumptions، support count و interval معتبر؛ CV R² احتمال confidence نیست |
| P1 | attribution | تعریف مدل attribution و touchpoint؛ همبستگی/last-touch از incrementality علّی جدا بماند |
| P1 | experiment/holdout | ساخت hypothesis، control/variant، randomization، allocation، duration، primary/guardrail metrics و توقف امن |
| P1 | uplift معتبر | uplift فقط با طراحی علّی مناسب و checks؛ گزارش effect، interval، support، power/uncertainty و limitations؛ fallback سادهٔ treated/control causal proof نیست |
| P1 | currency/refund correctness | currency normalization، FX source/time، refund/chargeback/tax و timezone با تست |
| P2 | segmentation و campaign comparison | segment builder، campaign/channel comparison، funnel و cohort drill-down |
| P2 | data quality/statistical guardrails | sample-ratio mismatch، leakage، missingness، novelty، survivorship و calibration checks |
| P2 | recommendations & audit | پیشنهاد اقدام با evidence، مالک، تاریخچهٔ تغییر و اندازه‌گیری نتیجهٔ پس از اقدام |
| P2 | revenue/cost dashboard | gross/net revenue، model cost، cost per 1,000 events/operations و measured contribution margin |
| P3 | integrations | connectorهای CRM/analytics/ad platforms با قرارداد و تست واقعی؛ نه فهرست لوگوهای بدون اتصال |

**Preview Revenue:** event import/health demo، cohort explorer، realized-vs-predicted LTV، experiment builder، lift report با دادهٔ synthetic، campaign comparison و recommendation/audit log.

**موانع/راستی‌آزمایی‌های باز:** event schema و اتصال واقعی، cohort واقعی، attribution، طراحی holdout، اعتبار uplift، uncertainty/calibration، refund/currency/timezone، CORS و هزینهٔ inference.

## 5. Matching Pack — از cosine similarity به recommender قابل اندازه‌گیری

**نمونه‌های بازار:** Recombee، Algolia AI Recommendations و Bloomreach Discovery.  
**کار اصلی خریدار:** پیشنهادهای مرتبط، امن و متنوع را در لحظه دریافت کند و اثرشان بر تعامل/تبدیل را اندازه بگیرد.

| اولویت | قابلیت مورد انتظار | معیار پذیرش |
|---|---|---|
| P0 | hard constraints و safety | قیود اجباری و policy قبل از ranking اعمال شوند؛ هیچ booster نتواند آن‌ها را دور بزند |
| P0 | privacy/tenant isolation | دادهٔ پروفایل حساس حداقلی، tenant-scoped access، retention/deletion و audit |
| P1 | catalog/profile ingestion | schema نسخه‌بندی‌شده، ویژگی‌های لازم، completeness/freshness، validation و حذف/به‌روزرسانی entity |
| P1 | interaction event pipeline | impression، view، like/dislike، click، match، conversion و feedback با event ID و recommendation ID |
| P1 | real-time top-K API | top-K با context، فیلتر، pagination، latency/error contract و fallback صریح |
| P1 | scenario/rules builder | هدف/placement، candidate filters، hard constraints، boosters، ranking strategy و version |
| P1 | explainability | دلیل قابل‌فهم برای پیشنهاد و عوامل مؤثر؛ score غیرکالیبره با برچسب روشن |
| P1 | cold-start | مسیر مشخص برای کاربر/مورد جدید؛ بدون IDهای ساختگی، score ثابت یا fallback گمراه‌کننده |
| P1 | diversity/novelty | کنترل تکرار و تنوع، محدودیت exposure و ارزیابی اثر |
| P1 | feedback loop | اتصال recommendation→impression→interaction→outcome و attribution end-to-end |
| P2 | offline evaluation | Recall@K، NDCG@K، coverage/diversity و baseline ثابت با dataset مجاز و split زمانی |
| P2 | online experiment | A/B/control، traffic split، guardrail و conversion/retention metrics؛ جدا از offline relevance |
| P2 | bias/fairness review | سنجش exposure و خطا در segmentهای مجاز؛ مستندسازی trade-offها و امکان opt-out |
| P2 | analytics | funnel، recommendation performance، cohort و feedback quality با support count |
| P3 | integrations | event connectors و SDKهای پرتقاضا با تست contract |

**Preview Matching:** synthetic profile/catalog explorer، scenario/rules editor، کارت top-K با explanation، like/dislike feedback، cold-start demo، diversity controls، analytics و A/B simulator.

**موانع/راستی‌آزمایی‌های باز:** top-K واقعی و نه صرفاً embedding؛ attribution با recommendation ID؛ engagement/revenue ثابت؛ cold-start؛ hard filters؛ diversity؛ feedback loop؛ bias/privacy؛ ارزیابی offline/online.

## 6. Safety Pack — محصول Trust & Safety با گیت دادهٔ غیرقابل دور زدن

**نمونه‌های بازار:** Besedo/Implio، Hive Moderation و Sightengine؛ برای API و safety controls نیز OpenAI Moderation و Azure AI Content Safety.  
**کار اصلی خریدار:** محتوای پرریسک را با سیاست‌های قابل تنظیم شناسایی و به مسیر درست allow/review/block ارجاع دهد، با امکان کنترل انسانی و حسابرسی.

| اولویت | قابلیت مورد انتظار | معیار پذیرش |
|---|---|---|
| P0 | حقوق داده و مدل | corpus/model/weights با مجوز تجاری و provenance/privacy روشن؛ بدون آن benchmark یا ادعای کیفیت ممنوع |
| P0 | fail-closed و tenant policy | outage/timeout/invalid model result به تصمیم امن و قابل review منجر شود؛ policy per tenant |
| P0 | upload safety | اندازه/MIME/streaming/concurrency limits، scan و جلوگیری از resource exhaustion |
| P1 | multi-category moderation | متن/تصویر و taxonomy مشخص؛ زبان/گونهٔ نوشتاری و ورودی‌های پشتیبانی‌شده دقیقاً مستند شوند |
| P1 | per-category policy/threshold | allow/review/block، آستانه‌های جدا، versioning، preview و rollback |
| P1 | human review queue | صف محتوا/گزارش، دلیل flag، context امن، اولویت، assignee و approve/reject/escalate |
| P1 | audit & appeals | reviewer action، audit trail، appeal/reversal، incident escalation |
| P1 | analytics | volume، auto/manual split، backlog، category/reason، latency/error/cost؛ quality فقط از benchmark قانونی |
| P2 | custom rules/workflow | phrase/domain/URL rules، batch action و workflow قابل تنظیم |
| P2 | operator roles | RBAC، assignment و workload metrics |
| P2 | multilingual Persian quality | فارسی رسمی/محاوره، Finglish، typo و code-switch فقط پس از corpus مجاز و sealed evaluation |
| P3 | specialized identity checks | هرگونه face/identity matching فقط به‌صورت محصول جدا و اختیاری پس از legal/privacy/consent review، نه قابلیت پیش‌فرض یا ادعای قطعی |

**Preview Safety:** overview، review queue، policy builder، audit/appeal flow و analytics فقط با دادهٔ Demo. Preview موجود در PR #7 است؛ باید gapهای واقعی نسبت به همین معیارها مشخص شوند.

**مانع سخت:** Issue #8 همچنان BLOCKED تا corpus فارسی قانونی/رضایت‌مند، annotation دوگانه/adjudication، sealed test، benchmark، privacy/legal، security، cold install، load/cost و GO مستند. Issue #9 و هر outreach، proposal کیفیت، ROI یا فروش Safety تا آن زمان ممنوع است. هیچ دادهٔ production یارسلام export یا استفاده نشود.

## 7. ترتیب اجرایی و Definition of Done

1. **Baseline و audit:** وضعیت زنده GitHub، همهٔ PR/branch/checkها، issueها و docs را بخوان؛ source audit را با endpoint/schema/dependency/model/test ثبت کن.
2. **P0 مشترک:** امنیت، tenant isolation، quota، install independence، privacy و supply-chain را ببند.
3. **SEO:** workflow واقعی AEO و technical audit امن؛ سپس preview، تست و مستندات.
4. **Revenue:** event/cohort/experiment/causal evaluation؛ سپس preview، تست و مستندات.
5. **Matching:** recommender + feedback loop + hard filters؛ سپس preview، تست و مستندات.
6. **Safety:** فقط کارهای مستقل از corpus را انجام بده؛ هر مرحلهٔ نیازمند corpus را BLOCKED نگه دار تا مالک/حقوق‌دار داده اقدام کند.
7. **Per-pack release gate:** هر پک جداگانه از unit, contract, regression, integration, UI, clean install, full inference, SBOM/licensing, security, privacy/retention/deletion, load, latency, error-rate و cost-per-1000 عبور کند.
8. **Final review:** release readiness و evidence هر پک ثبت شود؛ NO-GO تا عبور همهٔ شروط. فروش/انتشار فقط با GO مستند مالک.

یک قابلیت فقط وقتی Done است که:
- کد و API contract وجود داشته باشد؛
- تست مناسب آن قابلیت وجود داشته و روی آخرین SHA سبز باشد؛
- UI/Docs/Preview مربوط به همان قابلیت به‌روز باشد؛
- محدودیت‌ها، provenance، privacy و خطاها روشن باشند؛
- وضعیت آن در همین سند و `docs/status/COMMERCIALIZATION_STATUS.md` ثبت شده باشد.

## 8. Snapshot اجرایی هنگام ثبت این استراتژی

این snapshot بر اساس وضعیت GitHub خوانده‌شده در 2026-11-04 است و باید در اجرای بعدی دوباره از GitHub راستی‌آزمایی شود:

| کار | وضعیت هنگام ثبت | مرجع |
|---|---|---|
| تحقیق رقابتی SEO/Revenue/Matching | تحقیق desk-research ثبت شده؛ هنوز source audit و قابلیت اجرایی کامل نیست | PR #15 merged؛ `docs/COMPETITOR_PRODUCT_BENCHMARK_2026-11-04.md` |
| UX research و Safety preview | Preview تعاملی Safety موجود؛ سه Preview دیگر باقی است | PR #7 merged؛ `docs/COMPETITOR_UX_RESEARCH.md` |
| ممیزی source سه پک | یافته‌های اولیه ثبت شده؛ بررسی کامل tests/inference و gap register نهایی باقی است | Issue #16 |
| atomic quota reservation | PR #18 باز؛ نتیجهٔ نهایی checks/merge باید از GitHub بررسی شود | PR #18 |
| Safety dataset/benchmark | BLOCKED؛ هیچ corpus تجاری پذیرفته نشده | Issue #8 |
| Safety outreach/sales | BLOCKED تا GO #8 | Issue #9 |
| public release/GHCR/VPS | ممنوع تا release gates و مالک GO | `docs/RELEASE_GATES.md` |
| production YarSalam | خارج از دامنه؛ هیچ تغییر مجاز نیست | guardrails پروژه |

## 9. دستور اجباری برای اتوماسیون روزانه

در ابتدای **هر اجرای زمان‌بندی‌شده**:

1. ابتدا این سند را از `main` بخوان: `docs/COMMERCIAL_PRODUCT_STRATEGY.md`.
2. سپس `docs/status/COMMERCIALIZATION_STATUS.md`، `docs/RELEASE_GATES.md`، `docs/COMMERCIAL_EXECUTION_SEQUENCE.md`، Issue #16، Issue #8، Issue #9، تمام PRهای باز، branchها و آخرین CI/logها را بخوان.
3. وضعیت واقعی GitHub را به‌روزتر از snapshot این سند بدان. قبل از هر تغییر، head SHA، diff، وضعیت PR و checks را دوباره بخوان.
4. یک **execution ledger** به نام `docs/status/COMMERCIALIZATION_STATUS.md` مرجع اصلی است: برای هر اقدام شناسه/قابلیت، وضعیت `DONE / IN_PROGRESS / BLOCKED / NOT_STARTED`، فایل/endpoint، PR/commit، تست و evidence ثبت کن. موارد DONE را دوباره اجرا نکن مگر regression یا drift واقعی پیدا شود.
5. از آخرین کار نیمه‌تمام و dependencyهای آن ادامه بده؛ اگر کار در حال اجرا یا PR باز وجود دارد، آن را دوباره نساز. ابتدا نتیجهٔ همان کار را پیگیری کن.
6. در هر اجرا یک چرخهٔ کوچک end-to-end را تا حد ممکن کامل کن؛ تغییرات backward-compatible، تست‌شده و در PR انجام شوند. branch drift فقط با merge commit واقعی و بدون force update رفع شود.
7. پس از هر تغییر معنادار، همین سند، execution ledger، issueها و PR description/status را همگام کن؛ ثبت کن چه چیزی انجام شد، چه چیزی در حال اجراست، گام بعدی دقیق چیست و چه مانعی نیازمند مالک است.
8. کارهای مستقل را به خاطر یک blocker متوقف نکن. هیچ‌گاه برای دادهٔ Safety از دادهٔ production یا dataset با مجوز نامعلوم استفاده نکن.
9. هیچ‌گاه public publish، GHCR، GitHub Release، فروش، outreach، production deploy یا تغییر زیرساخت یارسلام را انجام نده. گیت‌های Issue #8/#9 و `docs/RELEASE_GATES.md` لازم‌الاجرا هستند.
10. در گزارش به مالک فقط تغییر واقعی، PR/commit، نتیجهٔ تست و blocker مشخص را بگو؛ گزارش روزانهٔ تکراری یا ادعای موفقیت بدون evidence نفرست.

**نکتهٔ زمان‌بندی:** خارج از نوبت زمان‌بندی‌شده، این اتوماسیون نباید کار پس‌زمینهٔ پیوسته یا اجرای اضافه ادعا کند. نوبت بعدی از همین ledger ادامه می‌دهد و منتظر دستور تکراری «ادامه بده» نمی‌ماند.
