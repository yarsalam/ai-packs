<?php
/**
 * Plugin Name: YarSalam AI Products Preview
 * Description: Persian RTL product catalog and clearly-labelled static previews for YarSalam AI Packs.
 * Version: 0.1.0
 * Requires at least: 6.0
 * Requires PHP: 7.4
 * Author: YarSalam AI Labs
 * License: GPL-2.0-or-later
 * Text Domain: yarsalam-ai-products
 */

if (!defined('ABSPATH')) {
    exit;
}

final class YarSalam_AI_Products_Preview {
    const VERSION = '0.1.0';
    const SHORTCODE = 'yarsalam_ai_products';
    const PAGE_SLUG = 'ai-products';

    public static function init(): void {
        add_shortcode(self::SHORTCODE, [__CLASS__, 'render']);
        add_action('admin_menu', [__CLASS__, 'admin_menu']);
        add_action('admin_init', [__CLASS__, 'register_settings']);
        add_action('wp_enqueue_scripts', [__CLASS__, 'maybe_enqueue_assets']);
    }

    public static function activate(): void {
        $page = get_page_by_path(self::PAGE_SLUG);
        if (!$page) {
            $page_id = wp_insert_post([
                'post_title'   => 'محصولات هوش مصنوعی یارسلام',
                'post_name'    => self::PAGE_SLUG,
                'post_content' => '[' . self::SHORTCODE . ']',
                'post_status'  => 'publish',
                'post_type'    => 'page',
            ], true);

            if (!is_wp_error($page_id)) {
                update_option('yap_products_page_id', (int) $page_id, false);
            }
        }
    }

    public static function maybe_enqueue_assets(): void {
        if (!is_singular()) {
            return;
        }

        $post = get_post();
        if (!$post || !has_shortcode((string) $post->post_content, self::SHORTCODE)) {
            return;
        }

        wp_enqueue_style(
            'yap-showcase',
            plugins_url('assets/showcase.css', __FILE__),
            [],
            self::VERSION
        );
        wp_enqueue_script(
            'yap-showcase',
            plugins_url('assets/showcase.js', __FILE__),
            [],
            self::VERSION,
            true
        );
    }

    public static function register_settings(): void {
        register_setting('yap_settings_group', 'yap_contact_url', [
            'type' => 'string',
            'sanitize_callback' => 'esc_url_raw',
            'default' => '',
        ]);
        register_setting('yap_settings_group', 'yap_contact_email', [
            'type' => 'string',
            'sanitize_callback' => 'sanitize_email',
            'default' => '',
        ]);
    }

    public static function admin_menu(): void {
        add_options_page(
            'YarSalam AI Products',
            'AI Products Preview',
            'manage_options',
            'yap-products-preview',
            [__CLASS__, 'settings_page']
        );
    }

    public static function settings_page(): void {
        if (!current_user_can('manage_options')) {
            return;
        }
        ?>
        <div class="wrap">
            <h1>YarSalam AI Products Preview</h1>
            <p>این افزونه فقط کاتالوگ و نمونه‌های ثابت را نمایش می‌دهد؛ هیچ درخواست inference یا ارسال اطلاعات کاربر انجام نمی‌شود.</p>
            <form method="post" action="options.php">
                <?php settings_fields('yap_settings_group'); ?>
                <table class="form-table" role="presentation">
                    <tr>
                        <th scope="row"><label for="yap_contact_url">لینک تماس / درخواست پایلوت</label></th>
                        <td>
                            <input id="yap_contact_url" name="yap_contact_url" type="url" class="regular-text"
                                value="<?php echo esc_attr((string) get_option('yap_contact_url', '')); ?>"
                                placeholder="https://example.com/contact">
                            <p class="description">لینک صفحه تماس یا فرم درخواست همکاری را وارد کنید. این فیلد اختیاری است.</p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="yap_contact_email">ایمیل تماس</label></th>
                        <td>
                            <input id="yap_contact_email" name="yap_contact_email" type="email" class="regular-text"
                                value="<?php echo esc_attr((string) get_option('yap_contact_email', '')); ?>"
                                placeholder="team@example.com">
                            <p class="description">در صورت وارد کردن ایمیل، در انتهای صفحه نمایش داده می‌شود.</p>
                        </td>
                    </tr>
                </table>
                <?php submit_button('ذخیره تنظیمات'); ?>
            </form>
            <p><strong>صفحهٔ ساخته‌شده:</strong> <code>/<?php echo esc_html(self::PAGE_SLUG); ?>/</code></p>
        </div>
        <?php
    }

    public static function render(): string {
        $contact_url = esc_url((string) get_option('yap_contact_url', ''));
        $contact_email = sanitize_email((string) get_option('yap_contact_email', ''));
        $contact_href = $contact_url ? $contact_url : '#yap-contact';

        ob_start();
        ?>
        <div class="yap" dir="rtl" lang="fa">
            <section class="yap-hero">
                <div class="yap-hero__eyebrow">YARSALAM AI LABS <span>PRODUCT PREVIEW</span></div>
                <h1>هوش مصنوعی برای <em>کسب‌وکارهای واقعی</em></h1>
                <p class="yap-hero__lead">چهار خانواده محصول تخصصی؛ از کنترل محتوای کاربران تا تحلیل رشد، جست‌وجو و تطبیق. قابل اتصال از طریق API و قابل توسعه برای زیرساخت اختصاصی.</p>
                <div class="yap-hero__actions">
                    <a class="yap-button yap-button--primary" href="<?php echo $contact_href; ?>">درخواست همکاری برای پایلوت</a>
                    <a class="yap-button yap-button--quiet" href="#yap-products">مشاهده محصولات</a>
                </div>
                <div class="yap-hero__meta">
                    <span>API-first</span><span>قابل اتصال به اپ و وب</span><span>تمرکز بر زبان فارسی</span>
                </div>
            </section>

            <section class="yap-section" id="yap-products">
                <div class="yap-section__heading">
                    <div><span class="yap-kicker">PRODUCT CATALOG</span><h2>محصولات و وضعیت عرضه</h2></div>
                    <p>وضعیت‌ها شفاف‌اند: پیش‌نمایش فنی با محصول آماده فروش عمومی یکسان نیست.</p>
                </div>

                <div class="yap-grid">
                    <article class="yap-card yap-card--featured">
                        <div class="yap-card__top"><span class="yap-icon">🛡️</span><span class="yap-status yap-status--pilot">اولویت پایلوت</span></div>
                        <h3>Persian Trust &amp; Safety API</h3>
                        <p class="yap-card__subtitle">کنترل محتوای کاربرمحور برای محصولات فارسی</p>
                        <p>بررسی پیام، نظر، بیوگرافی و متن‌های ارسالی؛ همراه با سیاست اختصاصی هر کسب‌وکار و تصمیم سه‌حالته.</p>
                        <ul>
                            <li>قواعد اختصاصی مسدودسازی و ارجاع به بررسی</li>
                            <li>طبقه‌بندی اولیهٔ اسپم، تماس خارج از پلتفرم و موارد مشکوک</li>
                            <li>API برای سایت، اپلیکیشن و WordPress</li>
                            <li>مسیر توسعهٔ صف بازبینی و ثبت تصمیم مدیر</li>
                        </ul>
                        <div class="yap-card__foot"><span>وضعیت: آمادهٔ ارزیابی کنترل‌شده؛ benchmark مستقل و ممیزی نهایی باقی است.</span><a href="#yap-demo">دیدن نمونه ↓</a></div>
                    </article>

                    <article class="yap-card">
                        <div class="yap-card__top"><span class="yap-icon">🔎</span><span class="yap-status">پیش‌نمایش فنی</span></div>
                        <h3>SEO &amp; AI Visibility</h3>
                        <p class="yap-card__subtitle">تحلیل فنی سایت و پایش حضور برند</p>
                        <p>چک‌لیست سلامت HTML، بررسی ساختار و زیرساخت AEO برای گزارش حضور برند در پاسخ‌های هوش مصنوعی.</p>
                        <ul>
                            <li>بررسی title، description، heading و canonical</li>
                            <li>پایش mention و تاریخچه برند</li>
                            <li>تحلیل شباهت موضوعی لینک‌ها</li>
                            <li>پیشنهادهای قابل اقدام برای تیم محتوا</li>
                        </ul>
                        <div class="yap-card__foot"><span>وضعیت: پیش‌نمایش فنی؛ پوشش و دقت پایش باید بنچمارک شود.</span></div>
                    </article>

                    <article class="yap-card">
                        <div class="yap-card__top"><span class="yap-icon">📈</span><span class="yap-status yap-status--dev">در حال توسعه</span></div>
                        <h3>Revenue Intelligence</h3>
                        <p class="yap-card__subtitle">تحلیل درآمد و بهینه‌سازی کمپین</p>
                        <p>زیرساخت تحلیل promotion، ارزش طول عمر مشتری و اثر کمپین؛ با تمرکز بر نتیجهٔ قابل‌اندازه‌گیری.</p>
                        <ul>
                            <li>تحلیل و مقایسه پیشنهادهای تبلیغاتی</li>
                            <li>پیش‌بینی LTV و احتمال تبدیل</li>
                            <li>تحلیل اثر افزایشی کمپین (Uplift)</li>
                            <li>بازخورد و پایش کیفیت مدل</li>
                        </ul>
                        <div class="yap-card__foot"><span>وضعیت: مدل‌ها به آموزش، ارزیابی مستقل و کالیبراسیون نیاز دارند.</span></div>
                    </article>

                    <article class="yap-card">
                        <div class="yap-card__top"><span class="yap-icon">🧩</span><span class="yap-status yap-status--dev">در حال توسعه</span></div>
                        <h3>Matching &amp; Support Intelligence</h3>
                        <p class="yap-card__subtitle">تطبیق، تحلیل زبان و پشتیبانی هوشمند</p>
                        <p>ابزارهای embedding، شباهت، تحلیل احساسات فارسی، دستیار و تحلیل تیکت برای محصولات تعاملی.</p>
                        <ul>
                            <li>Embedding و جست‌وجوی شباهت</li>
                            <li>تحلیل احساس و دسته‌بندی درخواست‌ها</li>
                            <li>پیشنهاد تطبیق برای سناریوهای تخصصی</li>
                            <li>تحلیل و اولویت‌بندی تیکت پشتیبانی</li>
                        </ul>
                        <div class="yap-card__foot"><span>وضعیت: نیازمند نصب تمیز، benchmark و آزمون کیفیت در دامنهٔ مشتری.</span></div>
                    </article>
                </div>
            </section>

            <section class="yap-demo" id="yap-demo">
                <div class="yap-demo__copy">
                    <span class="yap-kicker">ILLUSTRATIVE PREVIEW</span>
                    <h2>نمونهٔ گردش کار Safety</h2>
                    <p>در محصول نهایی، هر کسب‌وکار می‌تواند تعیین کند که چه محتوایی مجاز باشد، چه چیزی به بررسی انسانی برود و چه چیزی مسدود شود.</p>
                    <div class="yap-demo__notice">این بخش فقط نمونهٔ نمایشی و ثابت است؛ به مدل زنده وصل نیست و هیچ متنی را ارسال یا ذخیره نمی‌کند.</div>
                </div>
                <div class="yap-demo__panel">
                    <div class="yap-demo__panelhead"><span>نمونه پیام کاربر</span><span class="yap-live-dot">STATIC DEMO</span></div>
                    <div class="yap-demo__message" id="yap-demo-message">بیا ادامه صحبت رو بیرون از اپ در واتساپ انجام بدیم.</div>
                    <div class="yap-demo__buttons">
                        <button type="button" class="yap-sample is-active" data-sample="contact">تماس خارج از پلتفرم</button>
                        <button type="button" class="yap-sample" data-sample="clean">پیام عادی</button>
                        <button type="button" class="yap-sample" data-sample="custom">قاعده اختصاصی</button>
                    </div>
                    <div class="yap-demo__result" aria-live="polite">
                        <span class="yap-result-label">تصمیم نمونه</span>
                        <strong id="yap-demo-action">نیازمند بررسی انسانی</strong>
                        <p id="yap-demo-reason">دلیل نمونه: تلاش برای انتقال گفتگو به خارج از پلتفرم.</p>
                    </div>
                </div>
            </section>

            <section class="yap-section yap-how">
                <div class="yap-section__heading"><div><span class="yap-kicker">INTEGRATION</span><h2>چطور به محصول شما متصل می‌شود؟</h2></div></div>
                <div class="yap-steps">
                    <div><b>01</b><h3>اتصال API</h3><p>ارسال درخواست از backend سایت یا اپلیکیشن، بدون قرار دادن کلید محرمانه در مرورگر یا اپ کاربر.</p></div>
                    <div><b>02</b><h3>سیاست کسب‌وکار</h3><p>تعریف قواعد اختصاصی، سهمیه مصرف و نحوه برخورد با محتوای مشکوک.</p></div>
                    <div><b>03</b><h3>پایش و بهبود</h3><p>اندازه‌گیری کیفیت، خطاها و هزینه؛ سپس توسعه بر اساس داده و بازخورد واقعی.</p></div>
                </div>
            </section>

            <section class="yap-contact" id="yap-contact">
                <span class="yap-kicker">EARLY ACCESS</span>
                <h2>برای طراحی پایلوت با ما در ارتباط باشید</h2>
                <p>پایلوت‌ها با دامنه، سقف مصرف و معیار موفقیت مشخص انجام می‌شوند. دسترسی عمومی و خرید آنلاین هنوز فعال نشده است.</p>
                <?php if ($contact_url) : ?>
                    <a class="yap-button yap-button--primary" href="<?php echo $contact_url; ?>">درخواست جلسه / پایلوت</a>
                <?php elseif ($contact_email) : ?>
                    <a class="yap-button yap-button--primary" href="<?php echo esc_attr('mailto:' . $contact_email); ?>">ارسال درخواست</a>
                <?php else : ?>
                    <span class="yap-contact__hint">مدیر سایت می‌تواند لینک فرم تماس یا ایمیل را از مسیر تنظیمات ← AI Products Preview اضافه کند.</span>
                <?php endif; ?>
                <div class="yap-footnote">نسخهٔ نمایشی برای معرفی محصولات است؛ وضعیت هر قابلیت فقط پس از گذر از تست کیفیت، امنیت، مجوز مدل و پایلوت مشتری به «آماده فروش» تغییر می‌کند.</div>
            </section>
        </div>
        <?php
        return (string) ob_get_clean();
    }
}

YarSalam_AI_Products_Preview::init();
register_activation_hook(__FILE__, ['YarSalam_AI_Products_Preview', 'activate']);
