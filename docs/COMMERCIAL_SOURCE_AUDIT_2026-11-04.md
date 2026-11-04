# ممیزی منبع و شکاف‌های واقعی محصول — 2026-11-04

**مخزن:** `yarsalam/ai-packs`  
**مرجع بسته‌بندی upstream فعلی:** `yarsalam/mobApp@4344cb05afe461551e1bfdc379b26a3c0fedddd9`  
**آخرین main مشاهده‌شده در mobApp:** `da4acf20c9851bc4e7fd34b1dcc2094183246109`  
**وضعیت انتشار:** NO-GO؛ این سند ممیزی است، نه تأیید آمادگی فروش.

## 1. دامنه و روش

این ممیزی کد اجرایی Gatewayهای چهار پک و سرویس‌های upstream را بررسی می‌کند. برای ارزیابی محصول قابل‌توزیع، مرجع اصلی upstream همان SHA ثابتی است که workflow توزیع در `.github/workflows/distributions.yml` به‌طور پیش‌فرض checkout می‌کند؛ نه لزوماً `mobApp/main`.

- کد Gateway و پیکربندی Compose از `ai-packs/main` بررسی شد.
- سرویس‌های Python در `mobApp@49718c978cda59237b2c6a206bdbe301accda157` بررسی شدند؛ این همان ref پیش‌فرض workflow توزیع و workflow اعتبارسنجی Matching است.
- `scripts/validate_api_contracts.py` در workflow توزیع routeهای Gateway را با decoratorهای upstream تطبیق می‌دهد. workflow توزیع در PR #18 با موفقیت اجرا شده است.
- این بررسی static source audit است؛ جایگزین full inference، clean install، benchmark، security review یا آزمون بار نیست.

## 2. هشدار مهم دربارهٔ upstream drift

در زمان ممیزی:
- ref مورد استفادهٔ توزیع: `49718c978cda59237b2c6a206bdbe301accda157`، پیام commit: `Install HTML parser for URL audit regression tests`.
- `mobApp/main`: `da4acf20c9851bc4e7fd34b1dcc2094183246109`، پیام commit: `Fix Revenue LTV feature contract and fallback`.
- GitHub compare برای `49718...` به `da4acf...` وضعیت `diverged` و `ahead_by=1 / behind_by=24` برگرداند.

commit فعلی `mobApp/main` اصلاح مهم LTV را دارد: schema ورودی Revenue را flat می‌کند، URL داخلی را به پورت درست تغییر می‌دهد و fallback عدد ساختگی LTV را حذف می‌کند. اما چون دو تاریخچه diverged هستند و ref بسته‌بندی ۲۴ commit منحصربه‌فرد دارد، تغییر سادهٔ pin به main یا کپی انتخابی فایل‌ها ایمن نیست. **تا زمان reconcile واقعی تاریخچه و اجرای دوبارهٔ تمام contract/build tests، ref بسته‌بندی تغییر نکند.** این blocker به‌عنوان کار فنی ثبت می‌شود، نه درخواست فوری از مالک.

## 3. یافته‌های SEO Pack

| اولویت | یافتهٔ قابل اثبات در کد | اثر محصولی | کار لازم |
|---|---|---|---|
| P1 | `ai_aeo_tracker/core/aeo_tracker.py`: provider پیاده‌سازی‌شده فقط `openai` است؛ سایر providerها در docstring «آینده» هستند. | پایش چندموتوره‌ای که در بازار رقابتی مهم است هنوز ارائه نشده است. | connector واقعی و مستقل برای هر engine، نسخه/منبع/زمان پاسخ، خطا و پوشش engine در هر گزارش. |
| P1 | همان فایل، `_call_with_retry`: پس از تمام retryها `mentioned=false` همراه error برمی‌گرداند. | قطع سرویس یا خطای API می‌تواند به‌اشتباه «برند ذکر نشده» نمایش داده شود و share-of-voice را منحرف کند. | وضعیت سه‌حالتهٔ `mentioned / not_mentioned / unavailable`؛ خطا نباید وارد denominator نرخ mention شود. |
| P1 | تشخیص mention با جست‌وجوی substring نام برند در متن پاسخ انجام می‌شود؛ citation URL/source capture در این خروجی دیده نمی‌شود. | mentionهای مبهم/نام‌های مشابه و منبع ارجاع قابل ممیزی نیستند. | normalization، entity disambiguation، evidence span، citation/source metadata و human review. |
| P1 | `ai_backlink_quality/core/link_graph.py`: `trust-flow` با NetworkX PageRank روی edgeهای ارسالی caller محاسبه می‌شود؛ crawler/index یا دیتاست backlink مستقل در این مسیر وجود ندارد. | نام Trust Flow می‌تواند با معیار تجاری third-party اشتباه گرفته شود؛ کیفیت لینک واقعی و coverage اثبات نشده است. | یا نام‌گذاری شفاف به graph-PageRank heuristic تغییر کند، یا connector مجاز backlink data و provenance اضافه شود. |
| P1 | `ai_backlink_quality/core/topic_relevance.py`: در خطای embedding به‌جای error، مقدار `0.0` برمی‌گرداند. | خطای dependency از «شباهت موضوعی صفر» قابل تشخیص نیست. | error state/version، timeout و dependency health؛ مقدار صفر فقط برای محاسبهٔ موفق معتبر باشد. |
| P1 | `ai_seo_recommender/core/cf_model.py`: در نبود `implicit`، fallback محبوبیت اجرا می‌شود؛ cold-start و شکست recommend نیز popular items را برمی‌گردانند. | API ممکن است پاسخ معتبرنما بدهد درحالی‌که مدل personalized فعال نیست؛ وضعیت و کیفیت رتبه‌بندی قابل سنجش نیست. | پاسخ شامل model state، fallback reason، model revision و evaluation evidence؛ training job status پایدار و قابل مشاهده. |
| P1 | AEO history در Redis تا ۱۸۰ روز نگهداری می‌شود؛ cache شش ساعت است. | retention و حذف tenant/project به سیاست محصول متصل نیست. | retention قابل تنظیم، delete/export per project و audit بدون نگهداری غیرضروری پاسخ خام. |

**قرارداد URL audit:** در upstream pin فعلی route `POST /audit/url` وجود دارد و با Gateway `POST /seo/audit/url` منطبق است؛ این مورد در ممیزی به‌عنوان mismatch ثبت نمی‌شود. با این حال smoke test خودش به یک URL عمومی متصل می‌شود و برای اجرای قابل تکرار باید egress policy، SSRF/DNS-rebinding controls و mock/offline test نیز مستقل ارزیابی شوند.

## 4. یافته‌های Revenue Pack

| اولویت | یافتهٔ قابل اثبات در کد | اثر محصولی | کار لازم |
|---|---|---|---|
| P1 | `ai_revenue/predictor.py`: خروجی `confidence` همان میانگین CV R² است، نه احتمال کالیبره؛ در ref بسته‌بندی مقدار fallback هم confidence ثابت 0.3 و LTV ثابت 150 دارد. | خریدار ممکن است امتیاز CV را به‌عنوان احتمال اطمینان فردی بفهمد و fallback ساختگی را نتیجهٔ واقعی تصور کند. | خروجی model status و fallback reason؛ حذف عدد ساختگی؛ calibration و prediction interval فقط پس از ارزیابی مناسب. |
| P1 | همان predictor بازهٔ خروجی را با حاشیهٔ ثابت ±۱۵٪ می‌سازد. | این بازه prediction interval آماری نیست و پوشش تضمین‌شده ندارد. | interval کالیبره/quantile با coverage گزارش‌شده یا حذف بازه تا زمان اثبات. |
| P1 | `train_gb` ابتدا scaler را روی کل داده fit می‌کند و سپس cross-validation را روی دادهٔ scale‌شده انجام می‌دهد. | leakage آماری می‌تواند CV score را خوش‌بینانه کند. | Pipeline شامل scaler و estimator داخل هر fold؛ temporal/group split و baseline. |
| P1 | `ai_uplift/core/uplift_model.py`: در نبود EconML، میانگین outcome گروه treated منهای control به‌عنوان fallback برمی‌گردد. | اختلاف خام دو گروه لزوماً اثر علّی نیست؛ selection bias و confounding می‌تواند نتیجه را منحرف کند. | خروجی صریح `descriptive_difference`، عدم نام‌گذاری causal uplift، experiment/holdout، overlap/balance diagnostics و uncertainty. |
| P1 | مسیر training فعلی uplift ورودی عمومی data/treatment/outcome/features می‌گیرد و شواهد کافی از طراحی آزمایش، randomization، propensity یا کنترل confounder در API دیده نمی‌شود. | ادعای incrementality/causal lift بدون طراحی آزمایش قابل دفاع نیست. | experiment registry، assignment/control، sample-ratio checks، pre-analysis plan و گزارش interval/power. |
| P1 | `ai_feedback` پاسخ accuracy و feature importance می‌دهد؛ مسیر ارزیابی مستقل، calibration و leakage controls در این API اثبات نشده است. | accuracy آموزشی یا روی دادهٔ دیده‌شده نباید معیار محصولی تلقی شود. | held-out/temporal evaluation، calibration، support count، class balance و model revision. |
| P2 | Gateway plan limits و credit weights مقادیر provisional هستند؛ هزینهٔ واقعی per 1,000 inference هنوز اندازه‌گیری نشده است. | قیمت‌گذاری و gross margin واقعی قابل تعیین نیست. | workload مشخص، cost/latency/error report و سپس تعریف plan/entitlement. |

**اصلاح مهم در upstream فعلی:** commit `da4acf20...` در `mobApp/main` fallback ساختگی LTV را حذف و contract ورودی/URL را اصلاح کرده است؛ اما این commit در ref فعلی distribution نیست و به‌علت diverged history نباید بدون reconcile وارد build شود.

## 5. یافته‌های Matching Pack

| اولویت | یافتهٔ قابل اثبات در کد | اثر محصولی | کار لازم |
|---|---|---|---|
| P1 | `ml_service/services/recommendation.py`: اگر revenue signal موجود نباشد مقدار پیش‌فرض 0.35 استفاده می‌شود و engagement برای همهٔ candidateها ثابت 0.5 است. | ranking فعلی از engagement واقعی/رفتار کاربر بهره نمی‌برد و بخشی از score مصنوعی است. | event pipeline با impression/click/like/dislike/match/conversion و attribution به `recommendation_id`. |
| P1 | همان سرویس، cold-start می‌تواند از fallback پیش‌فرض ۵۰ شناسهٔ ثابت با score برابر 0.85 استفاده کند؛ match score در نبود embedding مقدار ثابت 0.45 می‌دهد. | پاسخ شبیه نتیجهٔ شخصی‌سازی‌شده است اما می‌تواند دادهٔ ساختگی/غیرشخصی باشد. | fallback باید فقط candidateهای واقعی و مجاز را برگرداند؛ status/reason روشن و بدون score ساختگی. |
| P1 | route توصیه‌گر candidate list می‌گیرد، اما hard constraints، policy filtering و diversity/novelty در مسیر `RecommendationService` بررسی‌شده اثبات نشده‌اند. | در محصولات حساس، صرف similarity کافی نیست و ممکن است پیشنهاد نامجاز یا تکراری تولید شود. | enforce کردن hard filters قبل از ranking، policy tests، diversity controls و explanation. |
| P1 | `/internal/track-events` یک `dict` عمومی می‌گیرد و در Redis Stream ذخیره می‌کند؛ schema نسخه‌بندی‌شده و تضمین idempotency/attribution در این route دیده نمی‌شود. | اتصال recommendation به نتیجهٔ واقعی و سنجش CTR/conversion قابل اتکا نیست. | event schema، event ID، recommendation ID، idempotency، retention/deletion و outcome join. |
| P2 | offline metrics مانند Recall@K/NDCG@K و online A/B/control در API مورد بررسی مشاهده نشدند. | کیفیت relevance و اثر تجاری مستقل از هم قابل ارزیابی نیستند. | baseline ثابت، temporal split، coverage/diversity و online experiment جداگانه. |

## 6. قابلیت‌های مشترک و تجاری

| اولویت | یافته | اقدام |
|---|---|---|
| P1 | هر Gateway در `validate_license` کلید، active، expiry و plan را بررسی می‌کند؛ فیلد `domain` هنگام ایجاد license ذخیره می‌شود اما در مسیر validation بررسی نمی‌شود. | قرارداد domain binding روشن شود؛ اگر جزو محصول است، header/claim معتبر، رفتار WordPress و تست cross-domain تعریف شود؛ اگر نیست، ادعای domain lock از UI/docs حذف شود. |
| P1 | PR #18 با merge commit `4c443e6...` رزرو quota را در هر چهار Gateway با Redis Lua اتمیک کرد؛ 429 دیگر counter را افزایش نمی‌دهد و تست concurrent با Redis واقعی در CI موفق شد. | کار بعدی: سیاست billing برای upstream timeout/5xx روشن شود؛ در حال حاضر reservation پیش از proxy انجام می‌شود و refund/settlement شکست upstream در این تغییر اضافه نشده است. |
| P1 | Usage endpoint و quota وجود دارند، اما اشتراک/پرداخت/تمدید/لغو و customer workspace کامل در این مسیر اثبات نشده است. | برای مدل self-hosted، entitlement/renewal و مدیریت License مستند و تست شود؛ اگر پرداخت در scope این محصول نیست، حذف آن از promise فروش. |
| P2 | WordPress pluginها settings و demo/admin screen دارند؛ وجود آن‌ها به‌تنهایی customer workspace کامل، billing، team RBAC، audit و lifecycle را اثبات نمی‌کند. | سه Preview آفلاین/ synthetic برای SEO، Revenue و Matching و سپس مسیر عملیاتی مشتری جداگانه ساخته و تست شود. |

## 7. کارهای اولویت‌بندی‌شدهٔ بعدی

1. **P0/P1 — Reconcile upstream pin:** تحلیل ۲۴ commit موجود در ref بسته‌بندی در برابر تاریخچهٔ فعلی mobApp؛ تصمیم مستند دربارهٔ cherry-pick/rebase/branch lineage؛ عدم تغییر خودکار pin تا قراردادها و buildها سبز شوند.
2. **P1 — Revenue correctness:** حذف fallbackهای عددی گمراه‌کننده، جداسازی CV score از confidence، اصلاح leakage و تعریف contract برای fallback/uncertainty؛ از ref معتبر و PR جدا.
3. **P1 — Matching correctness:** حذف candidateهای ساختگی و scoreهای ثابت؛ enforce hard constraints و افزودن event attribution.
4. **P1 — SEO trustworthiness:** status سه‌حالته برای AEO، provenance/citations، fallback/error separation و نام‌گذاری دقیق backlink graph heuristic.
5. **P1 — Commercial license/billing:** domain binding decision، usage settlement برای upstream failures، customer entitlement/lifecycle و measured cost.
6. **P2 — Preview و analytics:** SEO/Revenue/Matching offline previews با RTL/English و تمام empty/loading/error/stale states؛ هیچ اتصال به production.
7. **Safety:** Issue #8 همچنان BLOCKED تا corpus قانونی/رضایت‌مند، annotation/adjudication، sealed test و گیت‌های کامل؛ Issue #9 متوقف.

## 8. شواهد و مراجع source

- `ai-packs/.github/workflows/distributions.yml`: ref پیش‌فرض upstream و اجرای build/route-contract validation.
- `ai-packs/scripts/validate_api_contracts.py`: بررسی decorator routeهای Gateway و upstream.
- `mobApp/python-ai/services/ai_aeo_tracker/core/aeo_tracker.py`: provider و mention/error behavior.
- `mobApp/python-ai/services/ai_backlink_quality/core/link_graph.py` و `core/topic_relevance.py`: graph score و failure fallback.
- `mobApp/python-ai/services/ai_seo_recommender/core/cf_model.py`: popularity fallback و cold-start.
- `mobApp/python-ai/services/ai_revenue/predictor.py`: CV score، confidence و range.
- `mobApp/python-ai/services/ai_uplift/core/uplift_model.py`: mean-difference fallback.
- `mobApp/python-ai/services/ml_service/services/recommendation.py` و `routes/matching.py`: scoring، cold-start و event route.
- `ai-packs/{seo,revenue,matching,safety}-pack/gateway/main.py`: license validation و usage metering.

**محدودیت:** این ممیزی بر کد و قراردادهای قابل‌مشاهده استوار است؛ هنوز full inference، حقوق مدل/داده، privacy/retention/deletion، cold install، load، p95 latency، error rate و cost-per-1000 برای هر پک GO نشده‌اند.


## 9. پیشرفت اصلاح مشترک — PR #22

PR [#22](https://github.com/yarsalam/ai-packs/pull/22) پیاده‌سازی domain binding اختیاری را در هر چهار Gateway و WordPress client اضافه کرده است. در صورت ادغام:
- `domain="*"` برای سازگاری backward-compatible بدون محدودیت باقی می‌ماند.
- domain مشخص normalize و با `X-Site-Domain` مقایسه می‌شود؛ header غایب یا نامطابق قبل از quota meter رد می‌شود.
- WordPress host از `home_url()` ارسال می‌شود و Gateway header را به upstream model service forward نمی‌کند.
- تست‌ها و CI PHP syntax برای چهار plugin اضافه شده‌اند.

این کنترل فقط جلوگیری از استفادهٔ اشتباه/سادهٔ کلید روی دامنهٔ دیگر است؛ اثبات مالکیت دامنه یا DRM رمزنگاری‌شده نیست، زیرا holder کلید bearer می‌تواند header را جعل کند. وضعیت نهایی فقط پس از green شدن تمام checks آخرین SHA و ادغام PR #22 به DONE منتقل شود.


## 10. Upstream correction evidence — mobApp PR #6 head `e017905c39835c1da2ddb3e8fd5f6bcd4c8e745b`

The readiness branch now contains the following code/test corrections. These are upstream branch facts; the AI Packs distribution pin is updated in a separate PR and must not be treated as active until that PR's CI passes and merges.

- **AEO:** provider errors are `status=unavailable`, `mentioned=null`; errors are not cached; failed runs are excluded from mention-rate denominators; all-failed response is HTTP 503. Regression tests cover legacy cached failures and partial/all-unavailable cases.
- **Matching:** fabricated cold-start candidate IDs and static 0.85 scores removed; fixed 0.35 revenue and 0.5 engagement defaults removed; fixed 0.45 match-score fallback removed. Only observed popularity within caller-provided candidate IDs can serve cold-start. Similarity/revenue components are explicit; missing revenue remains null; missing embeddings produce unavailable. Tests cover observed vs missing data and route behavior.
- **Revenue LTV:** StandardScaler is inside a Pipeline for CV folds; raw CV R² is preserved and labelled; fewer than 10 samples do not claim CV quality; confidence and fixed ±15% range are removed; intervals remain uncalibrated; old model CV provenance is marked legacy-unknown.
- **Revenue uplift:** treatment is validated as binary, minimum treated/control counts enforced, non-finite data rejected; fallback is descriptive group mean difference, not causal; no confidence interval is claimed; legacy fallback without sample counts is rejected. LinearDML output also carries `causal_claim=false` pending validated experiment design.

**Validation evidence on exact upstream head:** pack readiness 28 passed / 4 warnings; Revenue LTV model contract 8 passed.

**Still unresolved:** mobApp FeatureStoreRevenueService uses hard-coded/default values for several model features; no temporal/group split, calibrated intervals, randomized assignment provenance, real event/cohort pipeline, full model inference, clean install, load, latency or cost proof. Do not market the above code corrections as measured accuracy/uplift/ROI.


## 11. Safety WordPress request-path correction

A post-merge review of all authenticated WordPress request paths found that PR #22 had added `X-Site-Domain` to Safety multipart upload requests but missed the separate JSON request method. PR #24 adds the header to Safety JSON calls and strengthens CI to require both occurrences (JSON + multipart). Until PR #24 merges, do not treat Safety WordPress domain binding as complete.


## 12. AEO multi-engine adapter evidence — mobApp PR #6 head `4344cb05afe461551e1bfdc379b26a3c0fedddd9`

- OpenAI and Perplexity Sonar providers are supported through separate adapters. The default request runs every configured provider; callers may select engines explicitly.
- Results carry engine/model and provider citations; mention rates are calculated per engine only. Multi-engine requests deliberately set the legacy aggregate `mention_rate` to null.
- Missing keys, provider failures and unsupported engines produce `unavailable` with `mentioned=null`, excluded from mention-rate denominators.
- Exact-head tests: Python AI readiness 33 passed / 17 warnings; Revenue LTV contract 8 passed.
- Live Perplexity validation requires a test API key and is not yet complete. AI Packs compose/distribution env passthrough and SEO WordPress engine selection are being validated in PR #24/#25.


## 13. Current distribution source and historical-audit boundary — 2026-11-04

- AI Packs PR #24 merged as `0fe44582c4b9a673482319d4f11fb13d66dd6747`; all distribution, CI and validation-only image workflows now pin mobApp `4344cb05afe461551e1bfdc379b26a3c0fedddd9`.
- Sections 3–9 record the original static audit against `49718c978cda59237b2c6a206bdbe301accda157`; do not read those rows as a complete fresh audit of the new pinned SHA.
- Sections 10 and 12 record correction evidence on the readiness branch, including AEO unavailable semantics, Matching fabricated-fallback removal, Revenue uncertainty fixes and AEO multi-engine adapters.
- mobApp PR #6 remains Draft. The pin is reproducible and CI-validated, but that does not make the upstream PR merged or establish full inference, source licensing, clean install, load, latency or cost readiness.
- Remaining work is a fresh route/schema/model/test audit on the exact pinned SHA and verification that all shipped artifacts contain only that revision. No production deployment or public publishing occurred.


## 14. Revenue feature-store provenance audit — mobApp PR #6 head 9474b4ace1da44d6c2662b0554918ae521c7eaec

The current Revenue source still contains material synthetic/default feature values. This finding is independent of the predictor's CV leakage/confidence corrections and remains a P1 blocker for trustworthy LTV inference.

**Source:** `src/feature-store-rvenue/feature-store-rvenue.service.ts`, `python-ai/services/ai_revenue/app.py`, `python-ai/services/ai_revenue/predictor.py`, `src/revenue/revenue-attribution.service.ts`.

| Feature | Current source behavior | Product consequence | Required correction |
|---|---|---|---|
| channelType | Encoded from acquisitionSource; unknown values default to 0.5 | Partial real provenance, unknown conflated with average | Explicit unknown/missing state and mapping version |
| timeToConversion | Derived from first paid payment minus user.createdAt; no payment => 999 | Real but simplistic; cohort/late payment handling unverified | Explicit observation window and censoring/maturity semantics |
| ltv | Sum of paid IRT payments only in FeatureStoreRevenueService | Currency-limited; refund/chargeback handling not established | Currency-safe net revenue and refund/chargeback adjustment |
| cityWeight | User count in city divided by total-user heuristic | Proxy is not acquisition/revenue value | Remove unless independently validated; document denominator/time |
| intentScore | Fixed event-type weights over latest 50 events | Heuristic, not calibrated intent probability | Versioned feature definition, temporal window, evidence and validation |
| engagementDepth | Raw count of latest 1000 events | Count depends on retention/window and user activity age | Window-normalized event features and missingness metadata |
| keywordDifficulty | Hard-coded 0.5 in buildFeatures; helper returns 0/50 on missing/error | External data is not actually wired into model feature; error looks like a value | Connect real source or return unavailable; provenance/time/version |
| contentLength | Hard-coded 0.5 | Synthetic input | Real source or explicit missing |
| retentionImpact | Hard-coded 0.5 | Synthetic input | Cohort retention feature with observation window, or missing |
| campaignCost | Hard-coded 0 | CAC/cost cannot be inferred | Currency- and attribution-window-safe campaign spend; otherwise null |
| competitorPressure | Method always returns 0.3 | Synthetic input | Real licensed source and freshness or missing |
| seasonalityFactor | Fixed month buckets 1.3/1.5/0.8 | Unvalidated calendar heuristic | Fit/validate by market and temporal split or remove |
| segmentSize | Hard-coded 0.5 | Synthetic input | Real segment count/definition and point-in-time snapshot |
| CAC/payback | Defaults to 0 in feature store; attribution service deliberately returns null where cost units are unknown | Zero can be misread as free acquisition / instant payback | Keep null/unavailable until cost currency and attribution are valid |

Additional model contract concern:
- `LTVRequest` in `python-ai/services/ai_revenue/app.py` still supplies numeric defaults for the 12 model features. A caller omitting a feature can silently get a prediction based on synthetic defaults.
- `RevenuePredictor.predict_ltv` returns an uncalibrated prediction and no interval; this is correct uncertainty labeling, but it does not repair synthetic inputs.
- `RevenueAttributionService.calculateLTVBySource` returns null CAC/payback where SEO activity cost currency is undefined; preserve that behavior rather than inventing zero.
- Training endpoint requires `actualLtv`, but no production/customer data may be copied into public CI or a demo corpus.

**Required P1 remediation in a separate mobApp PR (backward-compatible):**
1. Add feature provenance/status alongside every model input: observed / derived / missing, source, as-of timestamp, window, units, transformation and feature revision.
2. Stop treating absent values as numeric 0.5/0/0.3. Use an explicit insufficient-data path or a versioned, validated imputation strategy with missingness indicators; never silently infer.
3. Fix currency/refund/chargeback and cohort maturity for realized LTV.
4. Remove or relabel heuristic intent/city/seasonality features; temporal/group split and leakage checks required.
5. Add contract tests proving omitted/unknown inputs cannot silently produce a normal-looking LTV estimate.
6. Run exact-head model readiness, full inference on synthetic/legal fixtures, clean install, load/latency/error and cost tests.

**Status:** BLOCKED for commercial LTV claims until the input contract/provenance is fixed and evaluated. The code is from mobApp PR #6's current candidate branch; no production database or customer data was accessed.


## 15. Matching recommendation/event contract audit — mobApp PR #6 head 9474b4ace1da44d6c2662b0554918ae521c7eaec

**Source:** `python-ai/services/ml_service/routes/matching.py` and `python-ai/services/ml_service/services/recommendation.py`.

Verified behavior:
- `RecommendIn` accepts only `user_id`, caller-supplied `candidates` and `limit`. The service deduplicates candidate IDs, removes the requesting user and caps candidate count.
- Cold-start fallback now uses only observed popular entities inside the caller-provided candidate allowlist; fabricated IDs and fixed scores were removed in the upstream PR. This is a meaningful correctness improvement.
- The current recommendation request does not carry a scenario/placement, policy context or structured hard-constraint contract. Candidate allowlist is not equivalent to domain-specific policy filtering (eligibility, exclusions, exposure limits or diversity).
- `/internal/track-events` accepts an untyped `dict`; Redis Stream stores the raw JSON payload and timestamp. No schema version, event ID, recommendation ID, idempotency key, actor/tenant binding, consent context or validated outcome join is enforced.
- `track_events` catches Redis write errors and only logs them; the route still returns `{"status":"accepted"}`. The caller can therefore receive success even when the event was not persisted.
- No scenario registry, control/variant assignment, A/B allocation validation or offline/online metric contract is present in these inspected routes.

**Required P1 remediation in a separate backward-compatible mobApp PR:**
1. Versioned event schema with event_id, recommendation_id, scenario/version, event type, actor/tenant, timestamp, consent context and idempotency.
2. Propagate persistence failure as a retryable non-2xx response; never acknowledge an event that was not stored.
3. Add explicit placement/scenario and hard constraints; enforce eligibility before ranking and test that no booster can bypass constraints.
4. Track impression → click/like/dislike → match/conversion outcomes with recommendation_id and deduplication.
5. Add offline Recall@K/NDCG@K/coverage/diversity against a fixed temporal split; separately add online control/variant with validated traffic allocation and guardrails.
6. Add tenant isolation, retention/deletion and audit for event data.

**Status:** Candidate allowlist/cold-start fallback correction is present in upstream PR #6; full scenario, hard-constraint and reliable attribution workflow remain NOT_STARTED/BLOCKED for commercial claims. No production event stream was read or modified.
