# مسیر امن تهیهٔ دیتاست فارسی Safety

**وضعیت بررسی:** 2026-11-03 — هیچ corpus عمومی تا این تاریخ برای benchmark تجاری یارسلام تأیید نشده است.

## ۱. نتیجهٔ بررسی منابع عمومی

- **NASEZA:** مخزن [amirivojdan/naseza](https://github.com/amirivojdan/naseza) مجوز CC0-1.0 را اعلام می‌کند و README آن ۵٬۷۱۹ نمونهٔ فارسی با دو برچسب Normal/Offensive و منبع Telegram (کانال‌های سیاسی و هواداری ورزشی) را توضیح می‌دهد. متن CC0 خود تصریح می‌کند که affirmer مسئول clearing حقوق اشخاص ثالث یا اخذ رضایت‌های لازم نیست. بنابراین CC0 به‌تنهایی مبنای کافی برای privacy/data-protection و استفادهٔ این محصول نیست. فعلاً فقط candidate برای بررسی حقوقی است؛ در benchmark یا sealed test وارد نشود.
- **PHate:** مخزن [Zahra-D/Phate](https://github.com/Zahra-D/Phate) حدود ۷ هزار نمونه و splitهای train/validation/test را مستند می‌کند؛ GitHub repository metadata مقدار `license=null` دارد و README مجوز تجاری یا حقوق privacy/redistribution را اعلام نمی‌کند. انتشار عمومی مساوی اجازهٔ استفادهٔ تجاری نیست.
- **ParsHate:** مخزن [zbokaee/ParsHate](https://github.com/zbokaee/ParsHate) در metadata مقدار `license=null` دارد و README فعلی صریحاً می‌گوید داده «for research only» منتشر شده است؛ بنابراین برای benchmark تجاری مجاز نیست. رخصت CC-BY مقالهٔ EMNLP 2026 را نباید به‌عنوان مجوز dataset تفسیر کرد. Root مخزن فعلاً فقط README دارد و فایل corpus در آن نیست.
- **ParsCN:** مخزن [zahrasafdari/ParsCN](https://github.com/zahrasafdari/ParsCN) در README مجوز CC BY 4.0 را برای dataset/code اعلام می‌کند، اما GitHub metadata و Zenodo record فعلی license metadata خالی دارند. این مجموعه فقط ۱٬۱۰۰ جفت hate-speech/counter-narrative دارد: ۴۵۰ نمونه از PHATE، ۱۵۰ نمونهٔ ترجمه/اقتباس‌شده از MultiTarget-CONAN و ۵۰۰ نمونهٔ LLM-generated با منابع PHATE/MT-CONAN/HateXplain. تا وقتی صاحب‌حق، زنجیرهٔ مجوز منابع پایه، شرایط پلتفرم، privacy/consent و حق استفادهٔ تجاری/redistribution را کتبی تأیید نکنند، این ادعای CC BY برای پاک‌کردن حقوق منابع upstream کافی نیست؛ فقط candidate برای بررسی حقوقی است و وارد benchmark/sealed test نشود. پوشش آن نیز taxonomy کامل محصول را ندارد.

این منابع همچنین taxonomy کامل محصول (spam تجاری، انتقال ارتباط بیرونی، آزار، تهدید، محتوای سالم و موارد مبهم) و توزیع dating/social فارسی را به‌تنهایی پوشش نمی‌دهند. از آن‌ها برای ادعای کیفیت یا GO استفاده نکنید.

## ۲. مسیرهای مجاز جمع‌آوری

اولویت‌ها:

1. **همکاری با design partner:** قرارداد و data-processing terms پیش از انتقال؛ partner فقط داده‌ای را انتخاب کند که حق استفادهٔ آزمایشی و مبنای قانونی/رضایت معتبر دارد. نمونه‌گیری در محیط خصوصی partner انجام شود؛ export مستقیم از production یارسلام ممنوع است.
2. **پنل داوطلبان opt-in:** مشارکت‌کننده بداند متن برای چه هدفی، توسط چه کسانی، تا چه مدت و در چه محیطی پردازش می‌شود؛ رضایت قابل‌پس‌گرفتن و مسیر حذف داشته باشد. هیچ متن واقعی را به نام کاربر یا بدون رضایت تولید/جعل نکنید.
3. **دیتاست عمومی دارای مجوز:** مجوز دقیق dataset و نسخه، صاحب حق، منبع اولیه، شرایط پلتفرم، محدودیت تجاری، privacy basis و امکان redistribution را جداگانه بررسی کنید. اگر یکی نامعلوم است، corpus رد یا تا پاسخ کتبی معلق بماند.

Scraping از گروه/کانال خصوصی، پیام مستقیم، حساب نیازمند login یا محتوای production ممنوع است. عمومی بودن صفحه یا وجود یک مجوز copyright به‌تنهایی consent/privacy/terms را حل نمی‌کند.

## ۳. قرارداد داده و provenance

پیش از جمع‌آوری، در manifest خصوصی ثبت شود:

- صاحب داده و مسئول حقوقی؛ منبع و بازهٔ زمانی؛ روش انتخاب نمونه و محدودیت‌های sampling؛
- مجوز/قرارداد/consent، هدف مجاز، استفادهٔ تجاری، مدت نگه‌داری و حق حذف؛
- نام reviewer حقوقی/حریم خصوصی، تاریخ و شناسهٔ سند شواهد در سامانهٔ خصوصی؛
- نوع زمینه (message/bio/comment/profile)، تنوع زبانی و پوشش دسته‌ها؛
- شناسهٔ منبع/گروه pseudonymous و روش جداسازی source-group بین splitها.

سند consent، DPA، کلیدهای pseudonymization و نگاشت هویت در مخزن خصوصی محدود بمانند؛ هیچ‌کدام در مخزن عمومی commit نشوند.

## ۴. پاک‌سازی و annotation

1. فقط دادهٔ لازم را نگه دارید؛ نام، شماره، ایمیل، handle، URL شخصی، شناسه و اطلاعات غیرضروری حذف یا placeholder شود.
2. PII screening ماشینی + بازبینی انسانی انجام شود. اگر de-identification مطمئن نیست، نمونه حذف شود.
3. از `docs/PERSIAN_SAFETY_ANNOTATION_GUIDE_FA.md` استفاده کنید؛ حداقل دو annotator مستقل برای سهم اعلام‌شده و adjudication اختلاف‌ها لازم است.
4. برای هر نمونه `sample_id`، `source_group`، context، language varieties، labelهای annotator و label نهایی ذخیره شود. شناسه‌ها باید opaque باشند.
5. نمونه‌گیری فقط با کلیدواژهٔ توهین انجام نشود؛ نمونه‌های تصادفی/زمانی و موارد مرزی را هم در چارچوب مجاز پوشش دهید تا lexical shortcut ایجاد نشود.

## ۵. split و sealed test

- ابتدا بر اساس `source_group` (حساب/گفت‌وگو/منبع مشترک) به train، tune، validation و sealed_test تقسیم کنید؛ پیام‌های یک منبع نباید در چند split پخش شوند.
- sealed_test در دسترس توسعه‌دهندهٔ threshold نباشد؛ فقط پس از freeze مدل/pack اجرا شود.
- نسخهٔ dataset، manifest، guideline، model revision، pack commit و upstream service SHA ثابت و قابل بازتولید باشند.
- حداقل آغازین فعلی: ۱٬۰۰۰ رکورد کل و ۱۰۰ رکورد sealed test، همراه support حداقلی برای دسته‌ها/تنوع‌ها. این اعداد تضمین توان آماری نیستند و با نرخ رخداد/ریسک مشتری باید بازنگری شوند.

## ۶. ذخیره‌سازی و حذف

- داده و manifest فقط در فضای خصوصی رمزگذاری‌شده با دسترسی نقش‌محور و audit access ذخیره شوند.
- انتقال فقط با کانال رمزگذاری‌شده و دریافت‌کنندهٔ مجاز؛ فایل‌ها در GitHub public، CI artifact، issue، PR، demo یا chat عمومی قرار نگیرند.
- لاگ evaluator فقط شمارهٔ نمونه و نوع خطا را نشان دهد؛ report فقط aggregate metrics داشته باشد.
- retention deadline، مالک حذف و روش تأیید حذف برای فایل خام، نسخه‌های کاری، backup و خروجی annotation تعیین شود.
- sealed_test پس از تصمیم پایلوت نیز با همان کنترل دسترسی و retention نگه‌داری شود.

## ۷. اعتبارسنجی و اجرا

قالب manifest: `docs/templates/safety-benchmark-manifest.example.yaml`.

```bash
python scripts/validate_safety_benchmark.py \
  --manifest /secure/private/safety/manifest.yaml \
  --report /secure/private/safety/validation-summary.json
```

Validator مسیر manifest و splitها را خارج از checkout عمومی اجباری می‌کند، status حقوقی/حریم خصوصی، annotation/adjudication، حداقل نمونه، coverage، duplicate، source-group leakage و چند الگوی رایج PII را بررسی می‌کند. اسکن PII heuristic است و جای بازبینی انسانی را نمی‌گیرد.

پس از freeze مدل/pack و فقط با اجازهٔ دسترسی به sealed test:

```bash
export SAFETY_PACK_URL="https://your-isolated-test-gateway.example"
export SAFETY_PACK_LICENSE_KEY="(از secret store خصوصی)"
python scripts/evaluate_moderation.py \
  --dataset /secure/private/safety/sealed_test.jsonl \
  --output /secure/private/safety/sealed-test-report.json
```

کلید را در command line، GitHub Actions log یا فایل manifest قرار ندهید. Report aggregate را همراه با support count، revisionها، محدودیت‌ها و تصمیم go/no-go در فضای خصوصی ثبت کنید؛ فقط خلاصهٔ بدون دادهٔ خام و بدون اطلاعات محرمانه می‌تواند به issue عمومی منتقل شود.

## ۸. وضعیت blocker

تا زمان دریافت corpus دارای مجوز/رضایت و تکمیل privacy/legal review، benchmark واقعی، sealed test و Safety pilot شروع نمی‌شوند. ابزار و مسیر جمع‌آوری آماده‌سازی شده‌اند؛ نبود دادهٔ تأییدشده مانع واقعی فعلی برای مرحلهٔ benchmark است. Issue #9 تا GO مستند issue #8 بسته می‌ماند.
