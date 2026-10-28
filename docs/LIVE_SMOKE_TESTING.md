# آزمون زندهٔ AI Packs

**هدف:** بررسی مسیر واقعی Gateway → سرویس → inference برای هر پک، بعد از ساخت توزیع‌ها. این آزمون smoke test است؛ benchmark کیفیت مدل یا تأیید نهایی برای فروش نیست.

## پیش‌نیازها

- توزیع‌ها در `~/ai-packs/dist` ساخته و اعتبارسنجی شده باشند.
- Docker Engine و Docker Compose v2 نصب باشند.
- هر پک روی یک محیط آزمایشی/موقت اجرا شود؛ تست را روی دیتابیس/volume عملیاتی مشتری انجام ندهید.
- برای هر پوشهٔ پک، `.env.example` را به `.env` کپی کرده و `REDIS_PASSWORD` و توکن admin همان پک را با secret تصادفی قوی (حداقل ۳۲ کاراکتر) جایگزین کنید. مقدار `CHANGE_ME` برای اجرا مناسب نیست.
- برای سلامت کامل سرویس AEO در SEO Pack، مقدار معتبر `OPENAI_API_KEY` لازم است. بدون آن ممکن است health وضعیت degraded بدهد و endpoint مربوط به mentionها پاسخ 503 بدهد.

ساخت فایل‌های محیطی تصادفی برای چهار توزیع (این فرمان secretها را چاپ نمی‌کند):

```bash
python3 - <<'PY'
from pathlib import Path
import secrets

root = Path.home() / "ai-packs" / "dist"
packs = {
    "seo-pack": "SEO_PACK_ADMIN_TOKEN",
    "safety-pack": "SAFETY_PACK_ADMIN_TOKEN",
    "revenue-pack": "REVENUE_PACK_ADMIN_TOKEN",
    "matching-pack": "MATCHING_PACK_ADMIN_TOKEN",
}
for pack, admin_key in packs.items():
    folder = root / pack
    source = folder / ".env.example"
    target = folder / ".env"
    if not source.is_file():
        raise SystemExit(f"Missing {source}; build distributions first.")
    values = {}
    for line in source.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    values["REDIS_PASSWORD"] = secrets.token_hex(32)
    values[admin_key] = secrets.token_hex(32)
    if target.exists():
        # Keep a user-provided provider API key, but rotate the local test secrets.
        existing = {}
        for line in target.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                existing[key.strip()] = value.strip()
        if existing.get("OPENAI_API_KEY"):
            values["OPENAI_API_KEY"] = existing["OPENAI_API_KEY"]
    target.write_text("\n".join(f"{k}={v}" for k, v in values.items()) + "\n", encoding="utf-8")
    target.chmod(0o600)
    print(f"Prepared {target} (secrets hidden)")
PY
```

اگر قبلاً `.env` ساخته‌ای و `OPENAI_API_KEY` معتبر داخلش است، فرمان بالا آن مقدار را حفظ می‌کند؛ در غیر این صورت، برای SEO Pack آن را در `~/ai-packs/dist/seo-pack/.env` وارد کن. هیچ‌یک از فایل‌های `.env` را commit یا برای مشتری ارسال نکن.

## اجرای smoke test هر پک

هر بار فقط یک پک را روشن کن تا مصرف RAM و CPU مدل‌ها با هم جمع نشود. ابتدا SEO:

```bash
cd ~/ai-packs/dist/seo-pack
docker compose --env-file .env up -d --build
docker compose --env-file .env ps
cd ~/ai-packs
python3 scripts/smoke_test_packs.py --pack seo-pack --dist-dir ~/ai-packs/dist --timeout 180 --json-output ~/ai-packs/dist/smoke-seo.json
```

بعد همان الگو را برای `safety-pack`، `revenue-pack` و `matching-pack` اجرا کن؛ در فرمان تست فقط نام پک و نام فایل گزارش را عوض کن. پس از هر تست سرویس همان پک را متوقف کن، بدون حذف volume مدل‌ها:

```bash
cd ~/ai-packs/dist/seo-pack
docker compose --env-file .env down
```

پورت‌های پیش‌فرض Gatewayها روی loopback هستند: SEO `9000`، Safety `9001`، Revenue `9002` و Matching `9003`. اگر روی پورت/آدرس دیگری اجرا شدند از `--base-url` به همراه `--pack` استفاده کن.

تست برای هر پک health همهٔ سرویس‌های اعلام‌شده، ایجاد/اعتبارسنجی/revoke یک مجوز آزمایشی، یک مسیر inference واقعی و endpoint مصرف quota را بررسی می‌کند. کلید مجوز موقت چاپ نمی‌شود و پس از تست revoke می‌شود. نمونه‌های ورودی فقط دادهٔ ساختگی هستند.

### نمونه‌های تست

- **SEO:** درخواست HTTPS به `https://example.com/`، تحلیل metadata/heading/canonical/viewport/alt/links در HTML و سپس تست شباهت موضوعی دو متن با embedding.
- **Safety:** یک متن فارسی معمولی که باید از بررسی معنایی عبور کند، و یک مثال rule-based که شامل واژهٔ ممنوعه است.
- **Revenue:** رتبه‌بندی یک مجموعهٔ ساختگی از candidateهای promotion؛ پاسخ معتبر به‌تنهایی ثابت نمی‌کند مدل train شده یا scoreها کالیبره‌اند، چون سرویس می‌تواند fallback قاعده‌محور داشته باشد.
- **Matching:** embedding متن فارسی و اجرای مدل احساسات فارسی.

برای اجرای همهٔ تست‌ها یک‌جا، فقط زمانی از `--pack all` استفاده کن که هر چهار توزیع در حال اجرا و منابع کافی در دسترس باشند.

## تفسیر نتیجه

- کد خروجی `0`: همهٔ smoke checkهای انتخاب‌شده پاس شده‌اند و اسکریپت capability gap شناخته‌شده‌ای برای پک انتخاب‌شده گزارش نکرده است.
- کد خروجی `1`: حداقل یک smoke check اجرایی fail شده است. ابتدا `docker compose logs --tail=200` را در پوشهٔ همان پک بررسی کن.
- کد خروجی `2`: مسیرهای اجرایی پاس شده‌اند، اما شکاف قابلیت/آمادگی فروش گزارش شده است.

## محدودیت‌های فعلی پیش از عرضهٔ عمومی

1. SEO URL audit یک چک‌لیست تکنیکی HTML محدود است (پاسخ حداکثر ۱٫۵ MB، فقط HTTP(S) روی پورت پیش‌فرض و چند redirect)، نه crawler کامل، audit محتوا/لینک عمیق یا امتیاز رتبه‌بندی Google. DNS checks برنامه به‌تنهایی DNS rebinding را به‌طور کامل نمی‌بندد؛ پیش از انتشار عمومی، egress firewall/network policy باید دسترسی به شبکه خصوصی، loopback و metadata endpoints را مسدود کند.
2. پاسخ موفق Revenue می‌تواند از fallback قاعده‌محور باشد. برای محصول فروشی به دادهٔ واقعی و مجاز، مدل آموزش‌دیده، holdout زمانی/مستقل و کالیبراسیون نیاز است.
3. smoke test دقت مدل، false-positive/false-negative، latency در بار، هزینهٔ هر ۱۰۰۰ درخواست، شرایط مجوز مدل‌ها، صورتحساب/پرداخت، enforce شدن دامنهٔ license یا آمادگی حقوقی را تأیید نمی‌کند.
4. در اولین اجرا دانلود مدل‌ها و وابستگی‌ها می‌تواند سنگین باشد. اگر دانلود Hugging Face/سایت خارجی قطع شد، اتصال شبکه و نیاز به VPN را بررسی کن؛ خطای دانلود را به‌عنوان موفقیت inference حساب نکن.
