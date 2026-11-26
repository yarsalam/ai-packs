# ممیزی رقابتی Safety Pack و بازار فارسی‌زبان
**تاریخ بررسی:** ۲۶ نوامبر ۲۰۲۶  
**وضعیت:** پژوهش رومیزی بر پایهٔ منابع عمومی؛ نه مصاحبهٔ مشتری، تست محصول پولی یا ممیزی حقوقی.

## ۱. نتیجهٔ مدیریتی

دموی اولیه فقط داشبورد ایستا با سه رکورد و چند کنترل محلی بود؛ از نظر عمق workflow با محصولات بالغ بازار قابل رقابت نبود. نسخهٔ جدید دمو بر چرخهٔ کامل عملیات Trust & Safety بنا شده است: ingest، detection signals، tenant policy، allow/review/enforce، صف انسانی، پرونده و context، اقدام، audit، اعتراض، analytics، نقش‌ها و integration.

**نتیجهٔ بازار فارسی:** در جست‌وجوی عمومی، منابع پژوهشی فارسی و پروژه‌های متن‌باز/آزمایشی پیدا شد؛ اما شواهد کافی از یک SaaS ایرانی تثبیت‌شده با محصول سازمانی کامل شامل policy، صف انسانی، user-risk، appeals، audit و SLA پیدا نشد. این اثبات نبود رقیب نیست؛ ابزارهای خصوصی، پروژه‌های قراردادی یا محصولات کم‌نمایه ممکن است وجود داشته باشند. فیلترهای واژه و قابلیت‌های داخلی شبکه‌های اجتماعی، جانشین‌های ارزان و مهم‌اند. همچنین Respondology نشان می‌دهد حداقل یک vendor تجاری جهانی، Persian را در فهرست زبان‌های کامنت moderation خود اعلام کرده است؛ بنابراین ادعای «هیچ رقیب فارسی وجود ندارد» نادرست است.

**موضع پیشنهادی:** با ادعای «اولین/بهترین سامانهٔ تعدیل محتوای فارسی» وارد بازار نشویم. wedge پیشنهادی برای اعتبارسنجی: کنسول بازبینی انسانی و قواعد اختصاصی فارسی برای پلتفرم اجتماعی/دوطرفه، ابتدا در spam، انتقال گفتگو به بیرون، آزار و تهدید متنی. ادعای کیفیت مدل تا benchmark مستقل ممنوع.

## ۲. مقایسهٔ محصولات بین‌المللی

| محصول | شواهد عمومی محصول | قوت اصلی | پیام برای Safety Pack |
|---|---|---|---|
| Checkstep | چهار داشبورد Policy، Moderation، Compliance، Reporting؛ API ingest؛ confidence و rules؛ auto-enforce یا human review؛ ModBot؛ notice و appeal | policy منبع حقیقت است؛ چرخهٔ end-to-end؛ context و AI reasoning برای بازبین؛ compliance و reporting | محصول ما نباید فقط classifier باشد. policy، case workflow، appeals و reporting بخش اصلی محصول‌اند. |
| Hive Moderation Dashboard | custom rules برای post و user؛ action دستی/خودکار؛ review feed؛ high-risk users/posts؛ thresholds؛ reports، appeals، analytics، logs و Spam Manager | workflow عملیاتی، user-level rules، نقش‌ها، history و callback | تمایز بالقوه فقط با taxonomy و تجربهٔ فارسی/فینگلیش و vertical خاص، آن هم پس از اثبات کیفیت. |
| Besedo / Implio | در منابع عمومی ترکیب AI و human moderation برای marketplace/classifieds و چندرسانه‌ای توصیف شده | تناسب عمودی با آگهی و marketplace؛ rule و عملیات انسانی | ورود به marketplace نیازمند taxonomy اختصاصی آگهی/کلاهبرداری و مشتری واقعی است. |
| Alice (سابق ActiveFence) | محصول enterprise Trust & Safety و risk intelligence؛ تمرکز بر ریسک محتوا و کاربر | دید ریسک گسترده و enterprise | برای محصول اول بیش از حد وسیع؛ قابلیت‌های enterprise را فعلاً تقلید نکنیم. |
| Respondology / Moderate | ابزار تجاری مدیریت کامنت شبکه‌های اجتماعی؛ ترکیب keyphrase و business rules، generative AI و human moderation؛ analytics در سطح comment و اتصال به Instagram/Facebook/TikTok/YouTube/LinkedIn/Threads. صفحهٔ رسمی Persian را در فهرست زبان‌ها نام می‌برد. | نزدیک‌ترین رقیب تجاری یافت‌شده برای moderation فارسی در کامنت‌های social؛ لایهٔ انسانی و عملیات سریع؛ مدل SaaS و قیمت عمومی | تمرکز بر commentهای برند و کمپین، نه الزاماً پیام خصوصی و رفتار حساب در اپ دوست‌یابی. صفحهٔ FAQ از ۲۸ زبان و Persian نام می‌برد، صفحهٔ محصول جای دیگر ۱۰۰+ زبان می‌گوید و جدول قیمت Standard را English-only و Plus/Enterprise را چندزبانه می‌داند؛ پوشش واقعی فارسی و tier آن باید در demo فروشنده تأیید شود. ادعاهای سرعت/درصد vendor claims هستند. |
| FarsiShield (GitHub) | README از Persian/English/Finglish، normalization و evasion detection، lexicon، multi-tenant، API/SDK، policy editor، logs و analytics نام می‌برد | نمونهٔ متن‌باز مستقیم‌تر برای profanity فارسی و Finglish؛ نشان می‌دهد «فقط واژه‌نامه» تمایز نیست | در زمان بررسی ۰ ستاره/۰ fork، یک commit، مجوز مخزن نامشخص و فایل LICENSE قابل دریافت نبود. بلوغ، حقوق استفاده، امنیت و کیفیت مستقل تأیید نشده؛ رقیب تجاری اثبات‌شده محسوب نمی‌شود. |

Respondology را باید رقیب تجاری مستقیم‌تر برای کامنت شبکه‌های اجتماعی دانست؛ با این حال، use case آن با پیام‌های خصوصی و user-risk در پلتفرم‌های دوطرفه یکسان نیست. Checkstep و Hive صرفاً classifier نیستند؛ محصول اصلی آن‌ها سیستم تصمیم و عملیات است: policy، rule، context، صف، اقدام، تاریخچه، اعتراض، نقش و تحلیل.

منابع:
- Checkstep onboarding: https://training.checkstep.com/help/getting-started
- Checkstep content journey: https://training.checkstep.com/help/content-journey
- Hive dashboard: https://docs.thehive.ai/docs/what-is-the-moderation-dashboard
- Hive rules: https://docs.thehive.ai/docs/rules
- Hive appeals: https://docs.thehive.ai/docs/handle-appeals
- Hive actions/history: https://docs.thehive.ai/docs/actions
- Besedo: https://besedo.com/
- Alice: https://alice.io/llm
- Respondology Moderate: https://respondology.com/moderate/ و pricing: https://respondology.com/pricing-new/
- FarsiShield: https://github.com/mamathew98/farsi-shield

## ۳. بررسی نمونه‌های فارسی

### ParsHate — benchmark پژوهشی جدید
مقالهٔ EMNLP 2026 مجموعهٔ ۱۰٬۰۰۰ توییت فارسی از ۲۰۱۳ تا ۲۰۲۲ را معرفی می‌کند؛ ۳۱٪ نمونه‌ها hate speech هستند. annotation چندگانهٔ هدف در هفت گروه، تفکیک explicit/implicit، target و rationale در سطح span دارد. نتیجهٔ مدل‌های SOTA گزارش‌شده حدود ۷۹٪ F1 برای تشخیص hate و ۲۵٫۵٪ macro-F1 برای تشخیص هدف است.

**برداشت:** حتی در task محدود hate speech، تشخیص هدف بسیار دشوارتر از تشخیص کلی است؛ confidence واحد معادل فهم زمینه یا تشخیص قطعی تخلف نیست.

**مجوز:** عمومی بودن مقاله یا dataset به‌تنهایی مجوز تجاری، بازتوزیع یا نگهداری دادهٔ خام را ثابت نمی‌کند. مجوز و شروط dataset و upstream باید جداگانه بررسی شوند؛ تا آن زمان وارد sealed benchmark نشود.

منابع:
- ACL Anthology: https://aclanthology.org/2026.emnlp-main.1406/
- PDF: https://aclanthology.org/2026.emnlp-main.1406.pdf
- GitHub: https://github.com/zbokaee/ParsHate

### PHATE
بیش از ۷٬۰۰۰ نمونهٔ فارسی با برچسب چندگانه و rationaleهای annotator معرفی می‌کند؛ فایل‌های train/validation/test و annotationهای span/target در مخزن آمده‌اند. مجوز تجاری dataset از شواهد بررسی‌شده احراز نشده؛ مجوز مقاله یا دسترسی فایل جایگزین مجوز dataset نیست.
منبع: https://github.com/Zahra-D/Phate

### ParsCN
شامل ۱٬۱۰۰ جفت hate-speech / counter-narrative، شش گروه هدف و شش راهبرد پاسخ است. برای مطالعهٔ counter-narrative مفید است، اما benchmark عمومی spam، تماس بیرونی، تهدید یا رفتار حساب نیست. README مجوز CC BY 4.0 را اعلام می‌کند؛ زنجیرهٔ حقوق upstream هر نمونهٔ مشتق‌شده باید جداگانه بررسی شود.
منابع: https://github.com/zahrasafdari/ParsCN و https://zenodo.org/records/18266930

### Respondology / Moderate — رقیب تجاری با ذکر صریح Persian
صفحهٔ رسمی Moderate توضیح می‌دهد که محصول از سه لایهٔ keyphrase/business rules، generative AI و human moderators استفاده می‌کند؛ analytics در سطح هر comment و اتصال به شبکه‌های اجتماعی را ارائه می‌دهد. FAQ همان صفحه Persian را در فهرست زبان‌های پشتیبانی‌شده می‌آورد. در عین حال، منابع خود شرکت بین ۲۸ زبان و ۱۰۰+ زبان اختلاف دارند؛ جدول قیمت Standard را English-only و Plus/Enterprise را چندزبانه معرفی می‌کند. پس وجود Persian در FAQ به‌تنهایی اثبات نمی‌کند که در تمام پلن‌ها یا با کیفیت یکسان پوشش داده می‌شود؛ باید در demo و قرارداد پرسیده شود. این محصول برای comment moderation برندها و کمپین‌هاست و جایگزین مستقیم تمام نیازهای private-message moderation یا user-risk در dating/social apps نیست.
منابع: https://respondology.com/moderate/ ، https://respondology.com/platform-overview/ ، https://respondology.com/pricing-new/

### FarsiShield
README عمومی از normalization فارسی/عربی، تشخیص دورزدن واژه، lexicon فارسی/انگلیسی/Finglish، tenant، API key، policy editor، dashboard و Docker نام می‌برد. metadata عمومی در زمان بررسی: ایجاد سپتامبر ۲۰۲۶، یک commit، صفر star/fork، مجوز نامشخص و فایل LICENSE غیرقابل دریافت. ادعاهای README قابلیت پایدار یا تجاری را ثابت نمی‌کند. پیش از استفاده از کد/واژه‌نامه، مجوز و امنیت بررسی شود.
منبع: https://github.com/mamathew98/farsi-shield

### جانشین‌های موجود در ایران
فیلتر کلمات سفارشی و قابلیت‌های داخلی Instagram/شبکه‌های اجتماعی برای کسب‌وکار کوچک هزینهٔ تعویض نزدیک به صفر دارند؛ بنابراین محصول ما باید فراتر از blocklist ارزش بدهد. فهرست APIهای ایرانی، سرویس‌های عمومی متن‌کاوی و NLP فارسی را نشان می‌دهد، اما این با وجود یک محصول end-to-end Trust & Safety یکی نیست. در جست‌وجوی عمومی حاضر فروشندهٔ ایرانی با اسناد فنی روشن برای کنسول کامل سازمانی moderation پیدا نشد؛ این یافته محدود به منابع index‌شده است.
- راهنمای فیلتر کامنت: https://famix.ir/چگونه-کامنت-های-توهین-آمیز-اینستاگرام-را-به-صورت-خودکار-پنهان-کنیم/
- فهرست APIهای ایرانی: https://github.com/Hameds/APIs-made-in-Iran

## ۴. قابلیت‌های لازم برای محصول رقابت‌پذیر

| قابلیت | MVP عمودی | بعداً | فعلاً نسازیم |
|---|---|---|---|
| Inbox | فیلتر، اولویت، assignment، SLA، اقدام کنترل‌شده | routing پیشرفته | workforce optimization |
| Case detail | متن، context، report، history، reason، signals | conversation graph | explainability ادعایی |
| Policy engine | category، rule، threshold، allow/review/block | policy simulation و version diff | rule builder عمومی پیچیده |
| User risk | رخدادها، شمارنده‌ها، رفتار تکراری و توضیح | campaign detection | امتیاز پنهان و ban غیرقابل اعتراض |
| Actions | approve/remove/escalate/warn/temporary restriction با callback | bulk action و rollback | ban دائمی خودکار |
| Appeals | اعتراض، بازبینی مستقل، uphold/overturn | portal کاربر و SLA | ادعای compliance بدون بررسی حقوقی |
| Audit | event history، actor، policy version، reason | export و retention controls | گزارش انطباق ادعایی |
| Analytics | volume، category، queue time، overturn rate | QA sampling و drift | precision/recall ساختگی |
| Persian layer | normalizer، Persian/Finglish، ZWNJ، ارقام، evasion tests | لهجه و code-switch | ادعای پوشش کامل فارسی |
| Integration | REST API، webhook، idempotency، tenant key | SDKهای متعدد | marketplace و SSO زودهنگام |

## ۵. نقد و تکمیل دمو

نسخهٔ اولیه به‌دلیل داشتن چند KPI، سه ردیف ساختگی و policy preview، mockup بود نه نمایش محصول قابل خرید.

نسخهٔ جدید این بخش‌ها و تعاملات را نمایش می‌دهد:
- Overview: ورودی، backlog، رخدادهای اولویت‌دار و وضعیت تیم؛
- Inbox: جست‌وجو، فیلتر دسته/ریسک/وضعیت و بازکردن پرونده؛
- Case detail: متن/context، دلیل ارجاع، سیگنال‌ها، سابقه، گزارش، یادداشت و اقدام؛
- Users: سابقهٔ رفتاری و رخدادها با هشدار ضدتبعیض؛
- Appeals: اعتراض، دلیل کاربر و نتیجهٔ بازبینی؛
- Policies: دسته‌ها، toggle، threshold و نسخه‌بندی؛
- Analytics: جای خالی معیارهای اندازه‌گیری‌نشده؛
- Integration: شکل API، webhook، tenant و نقش‌ها.

تمام تعاملات HTML محلی‌اند و داده‌ها ساختگی. این UX prototype برای نقد طراحی است؛ backend، inference، persistence، جداسازی واقعی tenant، API، audit واقعی یا اقدام روی حساب واقعی ندارد.

## ۶. اولویت فنی

### P0 — قبل از هر ادعای محصول
1. corpus مجاز و مخصوص use case واقعی، نه صرفاً hate tweets؛
2. annotation guide با تفکیک نقض policy از اختلاف نظر، نقل‌قول، طنز، خبر و گفتگوی رضایتمندانه؛
3. sealed benchmark با split مبتنی بر source/user/time و گزارش per-class؛
4. normalization فارسی: ی/ي، ک/ك، نیم‌فاصله، کشیده، ارقام، emoji، فینگلیش و obfuscation؛
5. fail-safe: timeout یا unavailable مدل نباید بی‌صدا محتوا را block کند؛
6. privacy، retention، deletion، access control و security review؛
7. cold install، inference، load، latency و cost؛
8. audit trail و اعتراض واقعی.

### P1 — pilot candidate
1. یک API ingest و webhook callback پایدار؛
2. tenant و نقش‌های admin / lead / moderator / auditor؛
3. inbox و case detail با context؛
4. ruleهای محدود spam/off-platform/abuse/threat؛
5. actionها و audit event؛
6. appeal queue؛
7. analytics عملیاتی بدون ادعای کیفیت مدل.

### P2 — پس از اثبات تقاضا
چندرسانه‌ای، video/audio، campaign graph، QA پیشرفته، moderator wellbeing، transparency portal کامل، استقرار خصوصی و SLA سازمانی گسترده.

## ۷. wedge بازار و معیار توقف

گزینهٔ اول برای discovery: پلتفرم اجتماعی/دوطرفهٔ فارسی با پیام و پروفایل و درد عملیاتی مشخص در spam، انتقال مکالمه به بیرون، آزار تکرارشونده و تهدید.

این انتخاب تقاضا را تأیید نمی‌کند. باید خریدار، هزینهٔ فعلی moderation، حجم، willingness-to-pay و حق استفاده از داده روشن شود.

ادامه فقط با شریک طراحی واقعی، دادهٔ مجاز، توافق قبلی بر false-positive/negative و latency/cost، ارزش اقتصادی نسبت به ابزار فعلی و نبود blocker حقوقی/امنیتی. در غیر این صورت دامنه کوچک یا پروژه متوقف شود.

## ۸. ادعاهای ممنوع فعلی
- «بهترین مدل فارسی» یا «دقت ۹۹٪»؛
- پوشش کامل همهٔ گویش‌ها و فینگلیش؛
- کاهش قطعی هزینه یا نیروی انسانی؛
- انطباق قطعی با قوانین همهٔ کشورها؛
- تشخیص کلاهبردار یا نیت کاربر؛
- آمادگی production؛
- مجوز تجاری datasetهای پژوهشی بدون سند.

## ۹. منابع
1. Checkstep Getting Started — https://training.checkstep.com/help/getting-started
2. Checkstep Content Journey — https://training.checkstep.com/help/content-journey
3. Hive Moderation Dashboard — https://docs.thehive.ai/docs/what-is-the-moderation-dashboard
4. Hive Rules — https://docs.thehive.ai/docs/rules
5. Hive Appeals — https://docs.thehive.ai/docs/handle-appeals
6. ParsHate EMNLP 2026 — https://aclanthology.org/2026.emnlp-main.1406/
7. PHATE — https://github.com/Zahra-D/Phate
8. ParsCN — https://github.com/zahrasafdari/ParsCN
9. FarsiShield — https://github.com/mamathew98/farsi-shield
10. Iranian API directory — https://github.com/Hameds/APIs-made-in-Iran
11. Instagram comment filtering — https://famix.ir/چگونه-کامنت-های-توهین-آمیز-اینستاگرام-را-به-صورت-خودکار-پنهان-کنیم/

---
**تصمیم انتشار:** این سند و دمو مجوز release یا pilot ایجاد نمی‌کنند. تا رفع موارد Issue #8 و مانع Issue #9، دمو فقط synthetic و داخلی است.
