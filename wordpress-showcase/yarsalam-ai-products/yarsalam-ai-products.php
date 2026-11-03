<?php
/**
 * Plugin Name: YarSalam AI Products Preview
 * Description: Persian RTL product catalog and clearly-labelled static previews for YarSalam AI Packs.
 * Version: 0.2.0
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
    const VERSION = '0.2.0';
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
                            <li>بررسی دسته‌ای تا ۱۰۰ متن در هر درخواست</li>
                            <li>گزارش ماهانهٔ تجمیعی تصمیم‌ها، بدون ذخیرهٔ متن پیام</li>
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

            <section class="yap-workspace" id="yap-demo" aria-labelledby="yap-workspace-title">
                <div class="yap-workspace__intro">
                    <div>
                        <span class="yap-kicker">TRUST &amp; SAFETY WORKSPACE</span>
                        <h2 id="yap-workspace-title">محیط مدیریت و نظارت بر محتوا</h2>
                        <p>پیش‌نمایش تجربهٔ مدیر محصول و اپراتور امنیت؛ با داده‌های کاملاً ساختگی و بدون اتصال به مدل زنده.</p>
                    </div>
                    <span class="yap-preview-stamp"><i></i> پیش‌نمایش تعاملی</span>
                </div>

                <div class="yap-workspace__shell">
                    <aside class="yap-workspace__sidebar" aria-label="ناوبری پیش‌نمایش">
                        <div class="yap-workspace__brand"><span class="yap-brand-mark">Y</span><span><b>YarSalam</b><small>TRUST CENTER</small></span></div>
                        <div class="yap-workspace__tenant"><span class="yap-tenant-avatar">D</span><span><b>Demo Workspace</b><small>محیط نمایشی</small></span><span class="yap-tenant-chevron">⌄</span></div>
                        <span class="yap-workspace__nav-label">مدیریت محتوا</span>
                        <button type="button" class="yap-dash-tab is-active" data-yap-tab="overview" aria-pressed="true"><span>▦</span> نمای کلی</button>
                        <button type="button" class="yap-dash-tab" data-yap-tab="queue" aria-pressed="false"><span>☷</span> صف بررسی <em>۱۲</em></button>
                        <button type="button" class="yap-dash-tab" data-yap-tab="policies" aria-pressed="false"><span>⚙</span> سیاست‌ها و قوانین</button>
                        <div class="yap-sidebar-spacer"></div>
                        <div class="yap-workspace__sidebar-note"><span class="yap-sidebar-shield">✓</span><b>محافظت هوشمند</b><small>سیاست‌های اختصاصی هر کسب‌وکار</small></div>
                        <div class="yap-workspace__profile"><span class="yap-profile-avatar">م</span><span><b>مدیر نمونه</b><small>مدیر امنیت</small></span><span class="yap-profile-more">•••</span></div>
                    </aside>

                    <div class="yap-workspace__main">
                        <header class="yap-workspace__topbar">
                            <div class="yap-breadcrumb"><span>محیط کاری</span><b>/</b><strong data-yap-current-title>نمای کلی</strong></div>
                            <div class="yap-topbar-actions"><span class="yap-demo-chip">DEMO DATA</span><button type="button" class="yap-icon-button" aria-label="اعلان‌های نمونه">♧<i></i></button><span class="yap-topbar-avatar">م</span></div>
                        </header>

                        <div class="yap-workspace__content">
                            <div class="yap-workspace__notice"><span>ⓘ</span><span>محیط نمایشی است؛ اعداد، پیام‌ها و رویدادها ساختگی‌اند و هیچ تصمیمی روی کاربران واقعی اعمال نمی‌شود.</span></div>

                            <section class="yap-dash-panel is-active" data-yap-panel="overview">
                                <div class="yap-panel-heading"><div><span class="yap-date-label">گزارش نمونه · ۷ روز اخیر</span><h3>سلام، مدیر عزیز 👋</h3><p>نمایی از وضعیت امنیت و مدیریت محتوای پلتفرم شما</p></div><button type="button" class="yap-date-filter">۷ روز اخیر <span>⌄</span></button></div>

                                <div class="yap-kpi-grid">
                                    <article class="yap-kpi"><div><span>کل موارد بررسی‌شده</span><b class="yap-kpi-icon">▤</b></div><strong>۲٬۴۸۶</strong><small><i class="yap-trend-up">↗ ۱۲٪</i> نسبت به دوره قبل</small><div class="yap-kpi-spark yap-spark-a"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div></article>
                                    <article class="yap-kpi"><div><span>تأیید خودکار</span><b class="yap-kpi-icon yap-kpi-green">✓</b></div><strong>۲٬۱۷۴</strong><small><i class="yap-trend-up">↗ ۸٪</i> نسبت به دوره قبل</small><div class="yap-kpi-spark yap-spark-b"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div></article>
                                    <article class="yap-kpi"><div><span>نیازمند بررسی</span><b class="yap-kpi-icon yap-kpi-amber">◷</b></div><strong>۲۱۸</strong><small><i class="yap-trend-down">↘ ۳٪</i> نسبت به دوره قبل</small><div class="yap-kpi-spark yap-spark-c"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div></article>
                                    <article class="yap-kpi"><div><span>مسدودشده</span><b class="yap-kpi-icon yap-kpi-red">⊘</b></div><strong>۹۴</strong><small><i class="yap-trend-neutral">بدون تغییر</i> نسبت به دوره قبل</small><div class="yap-kpi-spark yap-spark-d"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div></article>
                                </div>

                                <div class="yap-analytics-grid">
                                    <article class="yap-widget yap-activity-widget">
                                        <div class="yap-widget-heading"><div><h4>روند فعالیت moderation</h4><p>توزیع تصمیم‌ها در بازهٔ انتخاب‌شده</p></div><span class="yap-widget-menu">•••</span></div>
                                        <div class="yap-chart-legend"><span><i class="yap-legend-total"></i> کل بررسی</span><span><i class="yap-legend-approved"></i> تأیید</span><span><i class="yap-legend-review"></i> بررسی انسانی</span></div>
                                        <div class="yap-bar-chart" role="img" aria-label="نمودار نمونه فعالیت هفت روز اخیر">
                                            <div class="yap-chart-grid"><span>۳۰۰</span><span>۲۰۰</span><span>۱۰۰</span><span>۰</span></div>
                                            <div class="yap-chart-columns">
                                                <div class="yap-chart-day"><div class="yap-bar-pair"><i style="--bar:68%"></i><i style="--bar2:52%"></i><i style="--bar3:12%"></i></div><small>ش</small></div>
                                                <div class="yap-chart-day"><div class="yap-bar-pair"><i style="--bar:78%"></i><i style="--bar2:63%"></i><i style="--bar3:15%"></i></div><small>ی</small></div>
                                                <div class="yap-chart-day"><div class="yap-bar-pair"><i style="--bar:55%"></i><i style="--bar2:43%"></i><i style="--bar3:10%"></i></div><small>د</small></div>
                                                <div class="yap-chart-day"><div class="yap-bar-pair"><i style="--bar:88%"></i><i style="--bar2:71%"></i><i style="--bar3:17%"></i></div><small>س</small></div>
                                                <div class="yap-chart-day"><div class="yap-bar-pair"><i style="--bar:73%"></i><i style="--bar2:57%"></i><i style="--bar3:14%"></i></div><small>چ</small></div>
                                                <div class="yap-chart-day"><div class="yap-bar-pair"><i style="--bar:96%"></i><i style="--bar2:76%"></i><i style="--bar3:19%"></i></div><small>پ</small></div>
                                                <div class="yap-chart-day"><div class="yap-bar-pair"><i style="--bar:62%"></i><i style="--bar2:49%"></i><i style="--bar3:11%"></i></div><small>ج</small></div>
                                            </div>
                                        </div>
                                    </article>

                                    <article class="yap-widget yap-category-widget">
                                        <div class="yap-widget-heading"><div><h4>دسته‌بندی موارد پرچم‌گذاری‌شده</h4><p>نمونهٔ تفکیک بر اساس نوع هشدار</p></div><span class="yap-widget-menu">•••</span></div>
                                        <div class="yap-category-list">
                                            <div><span><i class="yap-cat-dot yap-dot-spam"></i>اسپم و تبلیغات</span><b>۴۲٪</b><i class="yap-category-track"><i style="--fill:42%"></i></i></div>
                                            <div><span><i class="yap-cat-dot yap-dot-contact"></i>تماس خارج از پلتفرم</span><b>۲۸٪</b><i class="yap-category-track"><i style="--fill:28%"></i></i></div>
                                            <div><span><i class="yap-cat-dot yap-dot-abuse"></i>آزار و توهین</span><b>۱۸٪</b><i class="yap-category-track"><i style="--fill:18%"></i></i></div>
                                            <div><span><i class="yap-cat-dot yap-dot-other"></i>سایر موارد</span><b>۱۲٪</b><i class="yap-category-track"><i style="--fill:12%"></i></i></div>
                                        </div>
                                        <div class="yap-category-foot"><span>مجموع موارد پرچم‌گذاری‌شده</span><strong>۳۱۲ مورد</strong></div>
                                    </article>
                                </div>

                                <article class="yap-widget yap-recent-widget">
                                    <div class="yap-widget-heading"><div><h4>موارد اخیر نیازمند توجه</h4><p>آخرین موارد نمونه در صف بررسی</p></div><button type="button" class="yap-text-action" data-yap-go="queue">مشاهده همه موارد ←</button></div>
                                    <div class="yap-queue-head"><span>محتوا / شناسه</span><span>دسته‌بندی</span><span>سطح ریسک</span><span>وضعیت</span><span>اقدام</span></div>
                                    <div class="yap-queue-row" data-yap-row="contact"><div class="yap-queue-content"><span class="yap-content-avatar">م</span><span><b>«بیا در واتساپ ادامه بدیم…»</b><small>پیام · #MSG-2048</small></span></div><span class="yap-category-tag">تماس خارجی</span><span class="yap-risk yap-risk-medium">متوسط</span><span class="yap-state yap-state-review">در انتظار بررسی</span><button type="button" class="yap-row-action" data-yap-go="queue">بررسی</button></div>
                                    <div class="yap-queue-row" data-yap-row="spam"><div class="yap-queue-content"><span class="yap-content-avatar yap-avatar-orange">ا</span><span><b>«پیشنهاد ویژه و تبلیغ خدمات…»</b><small>بیوگرافی · #BIO-1032</small></span></div><span class="yap-category-tag">اسپم تبلیغاتی</span><span class="yap-risk yap-risk-high">بالا</span><span class="yap-state yap-state-blocked">مسدودشده</span><button type="button" class="yap-row-action" data-yap-go="queue">جزئیات</button></div>
                                    <div class="yap-queue-row" data-yap-row="clean"><div class="yap-queue-content"><span class="yap-content-avatar yap-avatar-purple">ن</span><span><b>«سلام، از آشنایی با شما خوشحالم…»</b><small>پیام · #MSG-2041</small></span></div><span class="yap-category-tag">محتوای عادی</span><span class="yap-risk yap-risk-low">پایین</span><span class="yap-state yap-state-approved">تأییدشده</span><button type="button" class="yap-row-action" data-yap-go="queue">جزئیات</button></div>
                                </article>
                            </section>

                            <section class="yap-dash-panel" data-yap-panel="queue" hidden>
                                <div class="yap-panel-heading"><div><span class="yap-date-label">مدیریت اپراتوری</span><h3>صف بررسی انسانی</h3><p>موارد مشکوک را بررسی و تصمیم نهایی را ثبت کنید.</p></div><span class="yap-queue-counter">۱۲ مورد در انتظار</span></div>
                                <div class="yap-queue-filters"><button type="button" class="is-selected" data-yap-filter="all">همه موارد <b>۱۲</b></button><button type="button" data-yap-filter="high">اولویت بالا <b>۳</b></button><button type="button" data-yap-filter="reported">گزارش‌شده <b>۴</b></button><button type="button" data-yap-filter="reviewed">بازبینی‌شده <b>۵</b></button></div>
                                <div class="yap-review-list">
                                    <article class="yap-review-card" data-review-card="contact" data-risk="medium" data-reported="1"><div class="yap-review-card__top"><span class="yap-risk yap-risk-medium">ریسک متوسط</span><small>#MSG-2048 · ۸ دقیقه پیش</small></div><h4>انتقال گفتگو به خارج از پلتفرم</h4><p class="yap-review-quote">«بیا در واتساپ ادامه بدیم و شماره‌تو برام بفرست.»</p><div class="yap-review-reasons"><span>دسته: تماس خارجی</span><span>سیگنال نمونه: شماره / پیام‌رسان خارجی</span><span>منبع: پیام خصوصی</span></div><div class="yap-review-actions"><button type="button" data-yap-decision="allow">تأیید محتوا</button><button type="button" data-yap-decision="review">ارجاع به بررسی</button><button type="button" data-yap-decision="block">مسدود کردن</button></div><div class="yap-review-feedback" aria-live="polite"></div></article>
                                    <article class="yap-review-card" data-review-card="spam" data-risk="high" data-reported="0"><div class="yap-review-card__top"><span class="yap-risk yap-risk-high">ریسک بالا</span><small>#BIO-1032 · ۲۱ دقیقه پیش</small></div><h4>الگوی تبلیغات و ارسال انبوه</h4><p class="yap-review-quote">«خدمات ویژه، پیشنهاد محدود و راه ارتباطی خارج از برنامه…»</p><div class="yap-review-reasons"><span>دسته: اسپم تبلیغاتی</span><span>سیگنال نمونه: الگوی تبلیغاتی</span><span>منبع: بیوگرافی</span></div><div class="yap-review-actions"><button type="button" data-yap-decision="allow">تأیید محتوا</button><button type="button" data-yap-decision="review">ارجاع به بررسی</button><button type="button" data-yap-decision="block">مسدود کردن</button></div><div class="yap-review-feedback" aria-live="polite"></div></article>
                                    <article class="yap-review-card" data-review-card="abuse" data-risk="medium" data-reported="0"><div class="yap-review-card__top"><span class="yap-risk yap-risk-medium">ریسک متوسط</span><small>#MSG-2015 · ۳۵ دقیقه پیش</small></div><h4>زبان توهین‌آمیز احتمالی</h4><p class="yap-review-quote">«یک پیام با عبارت نامناسب که نیازمند بررسی بافت گفتگو است.»</p><div class="yap-review-reasons"><span>دسته: آزار و توهین</span><span>سیگنال نمونه: واژگان مشکوک</span><span>منبع: گفت‌وگو</span></div><div class="yap-review-actions"><button type="button" data-yap-decision="allow">تأیید محتوا</button><button type="button" data-yap-decision="review">ارجاع به بررسی</button><button type="button" data-yap-decision="block">مسدود کردن</button></div><div class="yap-review-feedback" aria-live="polite"></div></article>
                                </div>
                                <p class="yap-panel-disclaimer">تمام موارد این صف ساختگی‌اند. اقدام‌ها فقط وضعیت نمونه را در همین صفحه تغییر می‌دهند.</p>
                            </section>

                            <section class="yap-dash-panel" data-yap-panel="policies" hidden>
                                <div class="yap-panel-heading"><div><span class="yap-date-label">کنترل کسب‌وکار</span><h3>سیاست‌ها و قوانین</h3><p>برای هر دسته، واکنش مناسب کسب‌وکار را تنظیم کنید.</p></div><span class="yap-policy-version">Policy v1 · نمونه</span></div>
                                <div class="yap-policy-intro"><span class="yap-policy-intro-icon">⚙</span><div><b>سیاست اختصاصی Demo Workspace</b><p>این تنظیمات صرفاً در مرورگر و برای نمایش تعامل پنل تغییر می‌کنند؛ به Gateway ذخیره نمی‌شوند.</p></div></div>
                                <div class="yap-policy-list">
                                    <article class="yap-policy-card"><div><span class="yap-policy-icon yap-dot-contact">↗</span><span><b>انتقال گفتگو به خارج از پلتفرم</b><small>تشخیص شماره، لینک و پیام‌رسان خارجی</small></span></div><label>اقدام پیش‌فرض</label><select data-yap-policy><option value="review" selected>ارجاع به بررسی انسانی</option><option value="block">مسدودسازی خودکار</option><option value="allow">اجازه عبور</option></select></article>
                                    <article class="yap-policy-card"><div><span class="yap-policy-icon yap-dot-spam">✳</span><span><b>اسپم و تبلیغات ناخواسته</b><small>الگوهای تکراری، لینک و پیام تبلیغاتی</small></span></div><label>اقدام پیش‌فرض</label><select data-yap-policy><option value="review">ارجاع به بررسی انسانی</option><option value="block" selected>مسدودسازی خودکار</option><option value="allow">اجازه عبور</option></select></article>
                                    <article class="yap-policy-card"><div><span class="yap-policy-icon yap-dot-abuse">!</span><span><b>آزار و تهدید</b><small>نیازمند بررسی بافت و شدت پیام</small></span></div><label>اقدام پیش‌فرض</label><select data-yap-policy><option value="review" selected>ارجاع به بررسی انسانی</option><option value="block">مسدودسازی خودکار</option><option value="allow">اجازه عبور</option></select></article>
                                </div>
                                <div class="yap-threshold-card"><div><div><b>آستانهٔ نمونه برای ارجاع</b><small>صرفاً نمایش تنظیم آستانه؛ امتیاز واقعی مدل نیست.</small></div><strong><output data-yap-threshold-value>۰٫۶۰</output></strong></div><input type="range" min="10" max="90" step="5" value="60" data-yap-threshold aria-label="آستانهٔ نمونهٔ ارجاع"><div class="yap-threshold-scale"><span>حساسیت بیشتر</span><span>ارجاع کمتر</span></div></div>
                                <div class="yap-policy-footer"><span>پیش‌نمایش محلی · بدون ذخیره‌سازی</span><button type="button" class="yap-button yap-button--primary" data-yap-policy-save>نمایش ثبت تنظیمات</button></div>
                                <p class="yap-policy-feedback" aria-live="polite"></p>
                            </section>
                        </div>
                    </div>
                </div>
                <div class="yap-workspace__disclaimer"><span>ⓘ</span> این داشبورد نمونهٔ رابط محصول است. آمار، صف، پیام‌ها و تصمیم‌ها ساختگی هستند؛ هیچ API زنده، حساب مشتری یا اطلاعات کاربری به آن متصل نیست.</div>
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
