<?php
/**
 * Plugin Name: YarSalam AI Products Preview
 * Description: Persian RTL product catalog and clearly-labelled static previews for YarSalam AI Packs.
 * Version: 0.3.0
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
    const VERSION = '0.3.0';
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
        add_menu_page(
            'YarSalam AI Packs',
            'AI Packs',
            'manage_options',
            'yap-ai-packs-console',
            [__CLASS__, 'console_page'],
            'dashicons-shield-alt',
            58
        );
        add_submenu_page(
            'yap-ai-packs-console',
            'وضعیت محصولات و CI',
            'وضعیت و CI',
            'manage_options',
            'yap-ai-packs-console',
            [__CLASS__, 'console_page']
        );
        add_submenu_page(
            'yap-ai-packs-console',
            'پیش‌نمایش محصولات',
            'پیش‌نمایش محصولات',
            'manage_options',
            'yap-products-preview',
            [__CLASS__, 'settings_page']
        );
    }

    private static function github_ci_snapshot(): array {
        $cached = get_transient('yap_ai_packs_ci_snapshot');
        if (is_array($cached)) {
            return $cached;
        }

        $response = wp_remote_get(
            'https://api.github.com/repos/yarsalam/ai-packs/actions/runs?per_page=20',
            [
                'timeout' => 10,
                'redirection' => 0,
                'headers' => [
                    'Accept' => 'application/vnd.github+json',
                    'X-GitHub-Api-Version' => '2022-11-28',
                    'User-Agent' => 'YarSalam-AI-Packs-Console',
                ],
            ]
        );

        if (is_wp_error($response)) {
            return ['error' => 'اتصال به GitHub برقرار نشد: ' . $response->get_error_message(), 'runs' => []];
        }
        $status = (int) wp_remote_retrieve_response_code($response);
        if ($status !== 200) {
            return ['error' => 'GitHub API با وضعیت HTTP ' . $status . ' پاسخ داد.', 'runs' => []];
        }

        $decoded = json_decode((string) wp_remote_retrieve_body($response), true);
        if (!is_array($decoded) || !isset($decoded['workflow_runs']) || !is_array($decoded['workflow_runs'])) {
            return ['error' => 'پاسخ GitHub قابل‌خواندن نبود.', 'runs' => []];
        }

        $snapshot = [
            'error' => '',
            'runs' => array_slice($decoded['workflow_runs'], 0, 15),
            'fetched_at' => time(),
        ];
        set_transient('yap_ai_packs_ci_snapshot', $snapshot, 5 * MINUTE_IN_SECONDS);
        return $snapshot;
    }

    private static function github_release_snapshot(): array {
        $cached = get_transient('yap_ai_packs_release_snapshot');
        if (is_array($cached)) {
            return $cached;
        }

        $response = wp_remote_get(
            'https://api.github.com/repos/yarsalam/ai-packs/releases?per_page=1',
            [
                'timeout' => 8,
                'redirection' => 0,
                'headers' => [
                    'Accept' => 'application/vnd.github+json',
                    'X-GitHub-Api-Version' => '2022-11-28',
                    'User-Agent' => 'YarSalam-AI-Packs-Console',
                ],
            ]
        );

        if (is_wp_error($response)) {
            return ['available' => false, 'error' => 'دریافت نسخهٔ GitHub ممکن نشد.'];
        }
        if ((int) wp_remote_retrieve_response_code($response) !== 200) {
            return ['available' => false, 'error' => 'GitHub Releases با خطا پاسخ داد.'];
        }

        $releases = json_decode((string) wp_remote_retrieve_body($response), true);
        if (!is_array($releases)) {
            return ['available' => false, 'error' => 'پاسخ Releases قابل خواندن نیست.'];
        }
        if (empty($releases)) {
            $snapshot = ['available' => false, 'error' => '', 'fetched_at' => time()];
            set_transient('yap_ai_packs_release_snapshot', $snapshot, 5 * MINUTE_IN_SECONDS);
            return $snapshot;
        }

        $latest = $releases[0];
        $snapshot = [
            'available' => !empty($latest['tag_name']),
            'tag' => isset($latest['tag_name']) ? sanitize_text_field((string) $latest['tag_name']) : '',
            'name' => isset($latest['name']) ? sanitize_text_field((string) $latest['name']) : '',
            'published_at' => isset($latest['published_at']) ? sanitize_text_field((string) $latest['published_at']) : '',
            'fetched_at' => time(),
        ];
        set_transient('yap_ai_packs_release_snapshot', $snapshot, 5 * MINUTE_IN_SECONDS);
        return $snapshot;
    }

    private static function private_control_snapshot(): array {
        $cached = get_transient('yap_ai_pack_private_status');
        if (is_array($cached)) {
            return $cached;
        }
        $base_url = defined('YAP_AI_PACK_CONTROL_URL') ? trim((string) YAP_AI_PACK_CONTROL_URL) : '';
        $token = defined('YAP_AI_PACK_CONTROL_TOKEN') ? (string) YAP_AI_PACK_CONTROL_TOKEN : '';
        if ($base_url === '' || strlen($token) < 48) {
            return ['connected' => false, 'error' => 'عامل خصوصی پیکربندی نشده است.'];
        }

        $parts = wp_parse_url($base_url);
        if (!is_array($parts) || empty($parts['host']) || !empty($parts['user']) || !empty($parts['pass']) ||
            !empty($parts['query']) || !empty($parts['fragment']) || (isset($parts['path']) && $parts['path'] !== '' && $parts['path'] !== '/')) {
            return ['connected' => false, 'error' => 'آدرس عامل خصوصی معتبر نیست.'];
        }

        $scheme = isset($parts['scheme']) ? strtolower((string) $parts['scheme']) : '';
        $host = (string) $parts['host'];
        $octets = filter_var($host, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4) ? array_map('intval', explode('.', $host)) : [];
        $private_ip = count($octets) === 4 && (
            $octets[0] === 10 ||
            ($octets[0] === 172 && $octets[1] >= 16 && $octets[1] <= 31) ||
            ($octets[0] === 192 && $octets[1] === 168)
        );
        if (!$private_ip || !in_array($scheme, ['http', 'https'], true)) {
            return ['connected' => false, 'error' => 'عامل فقط از طریق IP خصوصی RFC1918 و HTTP(S) قابل اتصال است.'];
        }

        $port = isset($parts['port']) ? (int) $parts['port'] : ($scheme === 'https' ? 443 : 80);
        if ($port < 1 || $port > 65535) {
            return ['connected' => false, 'error' => 'پورت عامل خصوصی معتبر نیست.'];
        }

        $url = $scheme . '://' . $host . ':' . $port . '/v1/status';
        $response = wp_remote_get($url, [
            'timeout' => 5,
            'redirection' => 0,
            'headers' => [
                'Accept' => 'application/json',
                'Authorization' => 'Bearer ' . $token,
            ],
        ]);
        if (is_wp_error($response)) {
            return ['connected' => false, 'error' => 'عامل خصوصی پاسخ نداد: ' . $response->get_error_message()];
        }
        if ((int) wp_remote_retrieve_response_code($response) !== 200) {
            return ['connected' => false, 'error' => 'عامل خصوصی پاسخ موفق نداد.'];
        }
        $body = json_decode((string) wp_remote_retrieve_body($response), true);
        if (!is_array($body) || !isset($body['memory'], $body['packs']) || !is_array($body['packs'])) {
            return ['connected' => false, 'error' => 'ساختار پاسخ عامل خصوصی معتبر نیست.'];
        }
        $snapshot = ['connected' => true, 'data' => $body, 'fetched_at' => time()];
        set_transient('yap_ai_pack_private_status', $snapshot, 30);
        return $snapshot;
    }

    public static function console_page(): void {
        if (!current_user_can('manage_options')) {
            return;
        }

        $snapshot = self::github_ci_snapshot();
        $release_snapshot = self::github_release_snapshot();
        $private_status = self::private_control_snapshot();
        $products = [
            ['name' => 'Persian Trust & Safety', 'status' => 'پیش‌نمایش تعاملی؛ پایلوت پس از Benchmark'],
            ['name' => 'SEO & AI Visibility', 'status' => 'پیش‌نمایش فنی؛ آزمون پوشش و امنیت باقی است'],
            ['name' => 'Revenue Intelligence', 'status' => 'در حال توسعه؛ آموزش و ارزیابی مدل باقی است'],
            ['name' => 'Matching & Support', 'status' => 'در حال توسعه؛ آزمون نصب و کیفیت باقی است'],
        ];
        ?>
        <div class="wrap">
            <h1>مرکز کنترل YarSalam AI Packs</h1>
            <p>نمای مدیریتی فقط‌خواندنی برای وضعیت محصولات و CI مخزن عمومی GitHub. این صفحه هیچ Workflow، استقرار، Secret یا سرویس عملیاتی را اجرا یا تغییر نمی‌دهد.</p>

            <style>
                .yap-console-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:18px 0}
                .yap-console-card{background:#fff;border:1px solid #dcdcde;border-radius:10px;padding:16px;min-width:0}
                .yap-console-card h2{font-size:14px;margin:0 0 8px}
                .yap-console-card p{color:#646970;margin:0;font-size:13px}
                .yap-console-muted{font-size:12px;color:#777;margin-top:10px}
                .yap-console-ok{color:#16804a;font-weight:700}.yap-console-warn{color:#a66b14;font-weight:700}
                .yap-console-table{background:#fff;border:1px solid #dcdcde;border-radius:8px;overflow:hidden}
                .yap-console-table table{border:0;margin:0}
                .yap-console-table th,.yap-console-table td{padding:10px 12px;vertical-align:middle}
                .yap-console-table td{font-size:12px}
                .yap-console-pill{display:inline-block;padding:3px 8px;border-radius:99px;background:#f0f0f1;color:#50575e;font-size:11px}
                .yap-console-pill.is-success{background:#e6f4ea;color:#137333}.yap-console-pill.is-failure{background:#fce8e6;color:#b3261e}.yap-console-pill.is-running{background:#e8f0fe;color:#2457a6}
                @media(max-width:900px){.yap-console-grid{grid-template-columns:1fr}}
            </style>

            <div class="yap-console-grid">
                <section class="yap-console-card">
                    <h2>محصولات</h2>
                    <p>۴ خانواده محصول در مخزن ثبت شده‌اند؛ هر کدام وضعیت عرضه و گیت‌های مستقل دارند.</p>
                    <div class="yap-console-muted">وضعیت دقیق هر محصول در جدول پایین آمده است.</div>
                </section>
                <section class="yap-console-card">
                    <h2>کیفیت مدل</h2>
                    <p class="yap-console-warn">Benchmark معتبر فارسی هنوز ثبت نشده است.</p>
                    <div class="yap-console-muted">تا پیش از ورود دادهٔ مجاز و اجرای ارزیابی، Precision/Recall/F1 و درصد دقت نمایش داده نمی‌شود.</div>
                </section>
                <section class="yap-console-card">
                    <h2>مصرف منابع سرور</h2>
                    <?php if (!empty($private_status['connected'])) :
                        $host_memory = $private_status['data']['memory'];
                        $available_mb = isset($host_memory['available_mb']) ? (int) $host_memory['available_mb'] : 0;
                        $total_mb = isset($host_memory['total_mb']) ? (int) $host_memory['total_mb'] : 0;
                    ?>
                        <p class="yap-console-ok">عامل خصوصی متصل است.</p>
                        <div class="yap-console-muted">RAM آزاد: <?php echo esc_html(number_format_i18n($available_mb)); ?> از <?php echo esc_html(number_format_i18n($total_mb)); ?> MB</div>
                        <div class="yap-console-muted">Swap آزاد: <?php echo esc_html(number_format_i18n((int) ($host_memory['swap_free_mb'] ?? 0))); ?> MB</div>
                    <?php else : ?>
                        <p class="yap-console-warn">متصل نیست.</p>
                        <div class="yap-console-muted"><?php echo esc_html($private_status['error'] ?? 'عامل خصوصی در دسترس نیست.'); ?></div>
                    <?php endif; ?>
                    <div class="yap-console-muted">اتصال فقط از سمت سرور WordPress به IP خصوصی انجام می‌شود؛ توکن در مرورگر ارسال یا نمایش داده نمی‌شود.</div>
                </section>
            </div>

            <h2>وضعیت محصولات</h2>
            <div class="yap-console-table">
                <table class="widefat striped">
                    <thead><tr><th>محصول</th><th>وضعیت</th></tr></thead>
                    <tbody>
                    <?php foreach ($products as $product) : ?>
                        <tr><td><strong><?php echo esc_html($product['name']); ?></strong></td><td><?php echo esc_html($product['status']); ?></td></tr>
                    <?php endforeach; ?>
                    </tbody>
                </table>
            </div>

            <?php if (!empty($private_status['connected'])) : ?>
                <h2 style="margin-top:26px">وضعیت سرویس‌های نصب‌شده</h2>
                <div class="yap-console-table">
                    <table class="widefat striped">
                        <thead><tr><th>پک</th><th>وضعیت</th><th>Containerهای در حال اجرا</th><th>Gateway</th><th>مصرف حافظهٔ Container</th></tr></thead>
                        <tbody>
                        <?php foreach (['safety-pack' => 'Safety', 'seo-pack' => 'SEO', 'revenue-pack' => 'Revenue', 'matching-pack' => 'Matching'] as $pack_id => $pack_label) :
                            $pack_data = $private_status['data']['packs'][$pack_id] ?? [];
                            $memory_rows = isset($pack_data['memory']) && is_array($pack_data['memory']) ? $pack_data['memory'] : [];
                            $memory_labels = [];
                            foreach ($memory_rows as $memory_row) {
                                if (!empty($memory_row['container']) && isset($memory_row['usage'])) {
                                    $memory_labels[] = (string) $memory_row['container'] . ': ' . (string) $memory_row['usage'];
                                }
                            }
                        ?>
                            <tr>
                                <td><strong><?php echo esc_html($pack_label); ?></strong></td>
                                <td><?php echo esc_html((string) ($pack_data['state'] ?? 'unknown')); ?></td>
                                <td><?php echo esc_html(number_format_i18n((int) ($pack_data['running_containers'] ?? 0))); ?></td>
                                <td><?php echo esc_html((string) ($pack_data['gateway']['status'] ?? 'unknown')); ?></td>
                                <td><?php echo esc_html($memory_labels ? implode(' · ', $memory_labels) : '—'); ?></td>
                            </tr>
                        <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php endif; ?>

            <h2 style="margin-top:26px">نسخهٔ منتشرشده</h2>
            <div class="yap-console-card">
                <?php if (!empty($release_snapshot['available'])) : ?>
                    <p class="yap-console-ok">آخرین نسخهٔ رسمی: <code><?php echo esc_html((string) $release_snapshot['tag']); ?></code></p>
                    <?php if (!empty($release_snapshot['name'])) : ?><div class="yap-console-muted"><?php echo esc_html((string) $release_snapshot['name']); ?></div><?php endif; ?>
                    <?php if (!empty($release_snapshot['published_at'])) : ?><div class="yap-console-muted">تاریخ انتشار: <?php echo esc_html(mysql2date(get_option('date_format'), (string) $release_snapshot['published_at'])); ?></div><?php endif; ?>
                <?php elseif (!empty($release_snapshot['error'])) : ?>
                    <p class="yap-console-warn"><?php echo esc_html((string) $release_snapshot['error']); ?></p>
                <?php else : ?>
                    <p class="yap-console-warn">هنوز هیچ GitHub Release رسمی منتشر نشده است.</p>
                    <div class="yap-console-muted">Artifactهای CI موقت‌اند؛ تا انتشار Release و عبور از گیت‌های کیفیت/امنیت، نسخهٔ رسمی فروش محسوب نمی‌شوند.</div>
                <?php endif; ?>
                <p style="margin-top:10px"><a href="https://github.com/yarsalam/ai-packs/releases" target="_blank" rel="noopener noreferrer">مشاهدهٔ نسخه‌ها در GitHub</a></p>
            </div>

            <h2 style="margin-top:26px">آخرین اجراهای GitHub Actions</h2>
            <?php if (!empty($snapshot['error'])) : ?>
                <div class="notice notice-warning"><p><?php echo esc_html($snapshot['error']); ?> <a href="https://github.com/yarsalam/ai-packs/actions" target="_blank" rel="noopener noreferrer">مشاهده Actions در GitHub</a></p></div>
            <?php elseif (empty($snapshot['runs'])) : ?>
                <div class="notice notice-info"><p>هنوز اجرای قابل‌نمایشی از GitHub دریافت نشده است.</p></div>
            <?php else : ?>
                <div class="yap-console-table">
                    <table class="widefat striped">
                        <thead><tr><th>Workflow</th><th>شاخه</th><th>وضعیت</th><th>نتیجه</th><th>آخرین به‌روزرسانی</th></tr></thead>
                        <tbody>
                        <?php foreach ($snapshot['runs'] as $run) :
                            $status = isset($run['status']) ? (string) $run['status'] : 'unknown';
                            $conclusion = isset($run['conclusion']) && $run['conclusion'] ? (string) $run['conclusion'] : '—';
                            $pill = $status === 'completed'
                                ? ($conclusion === 'success' ? 'is-success' : 'is-failure')
                                : 'is-running';
                            $run_url = isset($run['html_url']) ? esc_url($run['html_url']) : '';
                            $workflow_name = isset($run['name']) ? (string) $run['name'] : 'GitHub Actions';
                            $branch_name = isset($run['head_branch']) ? (string) $run['head_branch'] : '—';
                            $updated = isset($run['updated_at']) ? mysql2date(get_option('date_format') . ' ' . get_option('time_format'), $run['updated_at']) : '—';
                        ?>
                            <tr>
                                <td><?php if ($run_url) : ?><a href="<?php echo $run_url; ?>" target="_blank" rel="noopener noreferrer"><?php echo esc_html($workflow_name); ?></a><?php else : echo esc_html($workflow_name); endif; ?></td>
                                <td><code><?php echo esc_html($branch_name); ?></code></td>
                                <td><span class="yap-console-pill <?php echo esc_attr($pill); ?>"><?php echo esc_html($status); ?></span></td>
                                <td><?php echo esc_html($conclusion); ?></td>
                                <td><?php echo esc_html($updated); ?></td>
                            </tr>
                        <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
                <p class="yap-console-muted">دادهٔ CI از GitHub API عمومی دریافت می‌شود و حداکثر هر ۵ دقیقه تازه‌سازی خواهد شد. زمان دریافت: <?php echo !empty($snapshot['fetched_at']) ? esc_html(wp_date(get_option('date_format') . ' ' . get_option('time_format'), (int) $snapshot['fetched_at'])) : '—'; ?></p>
            <?php endif; ?>

            <p style="margin-top:20px"><a class="button button-primary" href="https://github.com/yarsalam/ai-packs/actions" target="_blank" rel="noopener noreferrer">رفتن به GitHub Actions</a> <a class="button" href="https://github.com/yarsalam/ai-packs" target="_blank" rel="noopener noreferrer">مخزن محصول</a></p>
        </div>
        <?php
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
                        <span class="yap-kicker">AI PRODUCT WORKSPACE</span>
                        <h2 id="yap-workspace-title">محیط کاری محصولات هوش مصنوعی</h2>
                        <p>چهار تجربهٔ محصولی در یک محیط نمایشی؛ داده‌ها ساختگی‌اند و هیچ بخشی به مدل یا API زنده متصل نیست.
                    </div>
                    <span class="yap-preview-stamp"><i></i> پیش‌نمایش تعاملی</span>
                </div>

                <div class="yap-workspace__shell">
                    <aside class="yap-workspace__sidebar" aria-label="ناوبری پیش‌نمایش">
                        <div class="yap-workspace__brand"><span class="yap-brand-mark">Y</span><span><b>YarSalam</b><small>AI PRODUCT SUITE</small></span></div>
                        <div class="yap-workspace__tenant"><span class="yap-tenant-avatar">D</span><span><b>Demo Workspace</b><small>محیط نمایشی</small></span><span class="yap-tenant-chevron">⌄</span></div>
                        <span class="yap-workspace__nav-label">مدیریت محتوا</span>
                        <button type="button" class="yap-dash-tab is-active" data-yap-tab="overview" aria-pressed="true"><span>▦</span> نمای کلی</button>
                        <button type="button" class="yap-dash-tab" data-yap-tab="queue" aria-pressed="false"><span>☷</span> صف بررسی <em>۱۲</em></button>
                        <button type="button" class="yap-dash-tab" data-yap-tab="policies" aria-pressed="false"><span>⚙</span> سیاست‌ها و قوانین</button>
                        <span class="yap-workspace__nav-label">محصولات دیگر</span>
                        <button type="button" class="yap-dash-tab" data-yap-tab="seo" aria-pressed="false"><span>⌕</span> SEO و دیده‌شدن AI</button>
                        <button type="button" class="yap-dash-tab" data-yap-tab="revenue" aria-pressed="false"><span>↗</span> هوشمندی درآمد</button>
                        <button type="button" class="yap-dash-tab" data-yap-tab="matching" aria-pressed="false"><span>◇</span> سیستم پیشنهادگر</button>
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

                            <section class="yap-dash-panel yap-product-preview" data-yap-panel="seo" hidden>
                                <div class="yap-panel-heading"><div><span class="yap-date-label">SEO &amp; AI VISIBILITY · دادهٔ ساختگی</span><h3>پایش دیده‌شدن در جست‌وجو و پاسخ‌های AI</h3><p>نمایش مسیر prompt → پاسخ → mention/citation → اقدام اصلاحی؛ نه گزارش زندهٔ موتورهای جست‌وجو.</p></div><span class="yap-queue-counter">DEMO ONLY</span></div>
                                <div class="yap-preview-state-switcher" role="group" aria-label="حالت‌های نمایشی SEO">
                                    <button type="button" data-yap-preview-state="seo:ready" aria-pressed="true">داده نمونه</button><button type="button" data-yap-preview-state="seo:loading" aria-pressed="false">بارگذاری</button><button type="button" data-yap-preview-state="seo:empty" aria-pressed="false">بدون داده</button><button type="button" data-yap-preview-state="seo:error" aria-pressed="false">خطا</button><button type="button" data-yap-preview-state="seo:stale" aria-pressed="false">داده کهنه</button>
                                </div>
                                <div data-yap-state-view="ready">
                                    <div class="yap-kpi-grid">
                                        <article class="yap-kpi"><div><span>نرخ mention نمونه</span><b class="yap-kpi-icon">◎</b></div><strong>۳۴٪</strong><small>محاسبهٔ ساختگی · نه سهم بازار واقعی</small></article>
                                        <article class="yap-kpi"><div><span>منابع citation نمونه</span><b class="yap-kpi-icon yap-kpi-green">↗</b></div><strong>۱۸</strong><small>منابع نمایشی برای طراحی UI</small></article>
                                        <article class="yap-kpi"><div><span>پرامپت‌های ردیابی‌شده</span><b class="yap-kpi-icon">⌕</b></div><strong>۴۰</strong><small>نمونهٔ prompt library</small></article>
                                        <article class="yap-kpi"><div><span>چک‌لیست فنی URL</span><b class="yap-kpi-icon yap-kpi-amber">✓</b></div><strong>۸/۱۱</strong><small>چک‌لیست heuristic، نه رتبهٔ Google</small></article>
                                    </div>
                                    <div class="yap-analytics-grid">
                                        <article class="yap-widget">
                                            <div class="yap-widget-heading"><div><h4>پوشش موتورهای پاسخ‌گو</h4><p>وضعیت اتصال باید برای هر engine مستقل و قابل مشاهده باشد.</p></div></div>
                                            <div class="yap-mini-table"><div><b>OpenAI</b><span class="yap-mini-status is-demo">نمونهٔ نمایشی</span><small>فقط یک provider در پیاده‌سازی فعلی بررسی شده است.</small></div><div><b>Claude</b><span class="yap-mini-status">هنوز متصل نشده</span><small>نیازمند connector، تست و provenance مستقل</small></div><div><b>Gemini</b><span class="yap-mini-status">هنوز متصل نشده</span><small>در این Preview دادهٔ زنده ندارد</small></div><div><b>Perplexity</b><span class="yap-mini-status">هنوز متصل نشده</span><small>در این Preview دادهٔ زنده ندارد</small></div></div>
                                        </article>
                                        <article class="yap-widget">
                                            <div class="yap-widget-heading"><div><h4>منابع ارجاع نمونه</h4><p>دادهٔ ساختگی برای نمایش جدول citation</p></div></div>
                                            <div class="yap-source-list"><div><b>example.com/guide</b><span>۶ ارجاع</span></div><div><b>docs.example.org</b><span>۴ ارجاع</span></div><div><b>blog.example.net</b><span>۳ ارجاع</span></div><div><b>news.example.test</b><span>۲ ارجاع</span></div></div>
                                        </article>
                                    </div>
                                    <article class="yap-widget">
                                        <div class="yap-widget-heading"><div><h4>اقدام‌های پیشنهادی بر اساس evidence</h4><p>هر پیشنهاد باید به URL، منبع و شواهد قابل بازبینی متصل باشد.</p></div></div>
                                        <div class="yap-action-list"><div><span class="yap-priority is-high">بالا</span><b>افزودن توضیح روشن برای موضوع «راهنمای خرید»</b><small>شاهد نمونه: صفحهٔ /guide در دو prompt نمایشی citation نشده است.</small></div><div><span class="yap-priority">متوسط</span><b>بازبینی عنوان و توضیح متای صفحه</b><small>شاهد نمونه: یک مورد از چک‌لیست فنی URL ناموفق است.</small></div><div><span class="yap-priority">متوسط</span><b>بررسی منبع رقیب</b><small>منبع و زمان نمونه‌گیری باید قبل از نتیجه‌گیری تأیید شوند.</small></div></div>
                                    </article>
                                </div>
                                <div class="yap-preview-state-card" data-yap-state-view="loading" hidden><b>در حال دریافت دادهٔ نمونه…</b><p>این حالت فقط برای آزمون طراحی loading است؛ هیچ درخواست شبکه‌ای ارسال نمی‌شود.</p><span class="yap-state-skeleton"></span><span class="yap-state-skeleton short"></span></div>
                                <div class="yap-preview-state-card is-empty" data-yap-state-view="empty" hidden><b>هنوز داده‌ای برای این پروژه ثبت نشده است.</b><p>پس از اتصال مجاز و اجرای اولین promptها، تاریخچه و citationها در این بخش نمایش داده می‌شوند.</p></div>
                                <div class="yap-preview-state-card is-error" data-yap-state-view="error" hidden><b>دریافت داده ناموفق بود.</b><p>خطای provider باید «نامشخص» ثبت شود، نه اینکه به‌عنوان عدم mention محاسبه شود.</p></div>
                                <div class="yap-preview-state-card is-stale" data-yap-state-view="stale" hidden><b>دادهٔ نمایش‌داده‌شده قدیمی است.</b><p>آخرین نمونه: ۲۴ ساعت قبل · نتیجهٔ stale نباید با وضعیت فعلی اشتباه شود.</p></div>
                                <p class="yap-panel-disclaimer">تمام اعداد و منابع این پنل ساختگی‌اند. در وضعیت محصول فعلی فقط provider OpenAI در کد بررسی‌شده پیاده‌سازی شده؛ سایر engineها در این صفحه صرفاً وضعیت هدف را نشان می‌دهند.</p>
                            </section>

                            <section class="yap-dash-panel yap-product-preview" data-yap-panel="revenue" hidden>
                                <div class="yap-panel-heading"><div><span class="yap-date-label">REVENUE INTELLIGENCE · دادهٔ ساختگی</span><h3>تحلیل درآمد، cohort و آزمایش</h3><p>تفکیک درآمد واقعی، پیش‌بینی مدل و نتیجهٔ آزمایش؛ این سه نوع داده نباید با هم مخلوط شوند.</p></div><span class="yap-queue-counter">DEMO ONLY</span></div>
                                <div class="yap-preview-state-switcher" role="group" aria-label="حالت‌های نمایشی Revenue">
                                    <button type="button" data-yap-preview-state="revenue:ready" aria-pressed="true">داده نمونه</button><button type="button" data-yap-preview-state="revenue:loading" aria-pressed="false">بارگذاری</button><button type="button" data-yap-preview-state="revenue:empty" aria-pressed="false">بدون داده</button><button type="button" data-yap-preview-state="revenue:error" aria-pressed="false">خطا</button><button type="button" data-yap-preview-state="revenue:stale" aria-pressed="false">داده کهنه</button>
                                </div>
                                <div data-yap-state-view="ready">
                                    <div class="yap-kpi-grid">
                                        <article class="yap-kpi"><div><span>درآمد ثبت‌شده</span><b class="yap-kpi-icon yap-kpi-green">↗</b></div><strong>۱۲٬۴۰۰</strong><small>واحد پولی ساختگی · actual demo</small></article>
                                        <article class="yap-kpi"><div><span>LTV مشاهده‌شده</span><b class="yap-kpi-icon">◉</b></div><strong>۳۲</strong><small>میانهٔ cohort نمونه · نه پیش‌بینی</small></article>
                                        <article class="yap-kpi"><div><span>Retention روز ۳۰</span><b class="yap-kpi-icon yap-kpi-amber">↻</b></div><strong>۴۲٪</strong><small>دادهٔ cohort ساختگی</small></article>
                                        <article class="yap-kpi"><div><span>آزمایش‌ها</span><b class="yap-kpi-icon">⚗</b></div><strong>۲</strong><small>یک draft · یک نمونهٔ بسته‌شده</small></article>
                                    </div>
                                    <div class="yap-analytics-grid">
                                        <article class="yap-widget">
                                            <div class="yap-widget-heading"><div><h4>عملکرد cohort نمونه</h4><p>مقادیر مشاهده‌شده، نه پیش‌بینی مدل</p></div></div>
                                            <div class="yap-mini-table"><div><b>هفتهٔ جذب ۱</b><span>روز ۷: ۷۱٪</span><small>روز ۳۰: ۴۲٪ · ۱۲۰ عضو نمونه</small></div><div><b>هفتهٔ جذب ۲</b><span>روز ۷: ۶۸٪</span><small>روز ۳۰: ۳۹٪ · ۹۸ عضو نمونه</small></div><div><b>هفتهٔ جذب ۳</b><span>روز ۷: ۷۴٪</span><small>روز ۳۰: داده ناکافی</small></div></div>
                                        </article>
                                        <article class="yap-widget">
                                            <div class="yap-widget-heading"><div><h4>وضعیت مدل LTV</h4><p>نمایش provenance و کیفیت مدل</p></div></div>
                                            <div class="yap-model-status"><span class="yap-mini-status is-warning">مدل نمونه · تأییدنشده</span><b>CV R² ≠ confidence probability</b><p>امتیاز cross-validation احتمال اطمینان فردی نیست. بازهٔ پیش‌بینی فقط پس از calibration معتبر نمایش داده شود.</p></div>
                                        </article>
                                    </div>
                                    <article class="yap-widget">
                                        <div class="yap-widget-heading"><div><h4>آزمایش و اثر افزایشی</h4><p>نتیجهٔ آزمایش باید با control، assignment و uncertainty گزارش شود.</p></div></div>
                                        <div class="yap-experiment-row"><div><b>نسخهٔ A / Control</b><span>۶۰۰ نمونهٔ ساختگی</span></div><div><b>نسخهٔ B / Treatment</b><span>۶۰۰ نمونهٔ ساختگی</span></div><div><b>تفاوت خام مشاهده‌شده</b><strong>+۶٫۴٪</strong><small>صرفاً اختلاف توصیفی؛ causal uplift تأیید نشده است.</small></div></div>
                                        <div class="yap-policy-footer"><span>گیت‌های بعدی: sample-ratio، balance، power و interval</span><span class="yap-mini-status">در انتظار ارزیابی</span></div>
                                    </article>
                                </div>
                                <div class="yap-preview-state-card" data-yap-state-view="loading" hidden><b>در حال محاسبهٔ گزارش نمونه…</b><p>حالت loading نمایشی است؛ هیچ مدل یا سرویس اجرا نمی‌شود.</p><span class="yap-state-skeleton"></span><span class="yap-state-skeleton short"></span></div>
                                <div class="yap-preview-state-card is-empty" data-yap-state-view="empty" hidden><b>رویداد درآمدی ثبت نشده است.</b><p>برای ساخت cohort باید eventهای نسخه‌بندی‌شده و دادهٔ actual revenue وارد شوند.</p></div>
                                <div class="yap-preview-state-card is-error" data-yap-state-view="error" hidden><b>منبع داده یا مدل در دسترس نیست.</b><p>در این وضعیت باید خطا و fallback reason نشان داده شود؛ عدد پیش‌بینی ساختگی تولید نشود.</p></div>
                                <div class="yap-preview-state-card is-stale" data-yap-state-view="stale" hidden><b>گزارش cohort به‌روز نیست.</b><p>آخرین به‌روزرسانی: ۲۴ ساعت قبل · actual و forecast از هم جدا بمانند.</p></div>
                                <p class="yap-panel-disclaimer">تمام اعداد ساختگی‌اند. تفاوت خام گروه‌ها اثر علّی نیست؛ هیچ ROI، uplift یا کیفیت پیش‌بینی واقعی ادعا نمی‌شود.</p>
                            </section>

                            <section class="yap-dash-panel yap-product-preview" data-yap-panel="matching" hidden>
                                <div class="yap-panel-heading"><div><span class="yap-date-label">MATCHING INTELLIGENCE · دادهٔ ساختگی</span><h3>موتور پیشنهاد و توضیح‌پذیری</h3><p>قیود اجباری پیش از ranking، سپس relevance، تنوع و اتصال نتیجه به feedback.</p></div><span class="yap-queue-counter">DEMO ONLY</span></div>
                                <div class="yap-preview-state-switcher" role="group" aria-label="حالت‌های نمایشی Matching">
                                    <button type="button" data-yap-preview-state="matching:ready" aria-pressed="true">داده نمونه</button><button type="button" data-yap-preview-state="matching:loading" aria-pressed="false">بارگذاری</button><button type="button" data-yap-preview-state="matching:empty" aria-pressed="false">بدون داده</button><button type="button" data-yap-preview-state="matching:error" aria-pressed="false">خطا</button><button type="button" data-yap-preview-state="matching:stale" aria-pressed="false">داده کهنه</button>
                                </div>
                                <div data-yap-state-view="ready">
                                    <div class="yap-kpi-grid">
                                        <article class="yap-kpi"><div><span>نامزدهای ورودی</span><b class="yap-kpi-icon">◎</b></div><strong>۱۲۰</strong><small>کاندیدهای ساختگی</small></article>
                                        <article class="yap-kpi"><div><span>پیشنهادهای Top-K</span><b class="yap-kpi-icon yap-kpi-green">◇</b></div><strong>۵</strong><small>برای یک سناریوی نمونه</small></article>
                                        <article class="yap-kpi"><div><span>عبور از قیود اجباری</span><b class="yap-kpi-icon yap-kpi-amber">✓</b></div><strong>۱۸/۲۴</strong><small>بقیه پیش از ranking حذف می‌شوند</small></article>
                                        <article class="yap-kpi"><div><span>پوشش event</span><b class="yap-kpi-icon">↻</b></div><strong>۷۲٪</strong><small>نمونهٔ نمایشی، نه telemetry واقعی</small></article>
                                    </div>
                                    <div class="yap-analytics-grid">
                                        <article class="yap-widget">
                                            <div class="yap-widget-heading"><div><h4>پیشنهادهای برتر</h4><p>دلیل پیشنهاد و وضعیت قیود برای هر مورد</p></div></div>
                                            <div class="yap-rec-list"><div><span class="yap-rec-rank">۱</span><span><b>نامزد نمونه A</b><small>علایق مشترک · تعامل اخیر · تنوع دسته</small></span><span class="yap-mini-status is-demo">مجاز</span></div><div><span class="yap-rec-rank">۲</span><span><b>نامزد نمونه B</b><small>شباهت محتوایی · بدون تکرار اخیر</small></span><span class="yap-mini-status is-demo">مجاز</span></div><div><span class="yap-rec-rank">۳</span><span><b>نامزد نمونه C</b><small>تطبیق زمینه · پوشش دستهٔ متفاوت</small></span><span class="yap-mini-status is-demo">مجاز</span></div></div>
                                        </article>
                                        <article class="yap-widget">
                                            <div class="yap-widget-heading"><div><h4>قیود و تنوع</h4><p>فیلترهای اجباری باید قبل از scoring اجرا شوند.</p></div></div>
                                            <div class="yap-filter-list"><div><span>شرایط اجباری</span><b>فعال</b></div><div><span>محدودیت تکرار</span><b>فعال</b></div><div><span>کنترل تنوع</span><b>نمونه</b></div><div><span>توضیح دلیل پیشنهاد</span><b>نمایشی</b></div></div>
                                        </article>
                                    </div>
                                    <article class="yap-widget">
                                        <div class="yap-widget-heading"><div><h4>چرخهٔ رویداد و نتیجه</h4><p>اتصال impression → interaction → outcome برای اندازه‌گیری عملکرد</p></div></div>
                                        <div class="yap-event-funnel"><div><b>۱٬۰۰۰</b><span>Impression</span></div><i>→</i><div><b>۲۸۰</b><span>Interaction</span></div><i>→</i><div><b>۸۴</b><span>Outcome</span></div></div>
                                        <p class="yap-panel-disclaimer">در نسخهٔ واقعی هر event باید event_id و recommendation_id داشته باشد و قابل deduplicate و ممیزی باشد.</p>
                                    </article>
                                </div>
                                <div class="yap-preview-state-card" data-yap-state-view="loading" hidden><b>در حال ساخت پیشنهادها…</b><p>حالت loading صرفاً برای نمایش UI است؛ هیچ مدل اجرا نمی‌شود.</p><span class="yap-state-skeleton"></span><span class="yap-state-skeleton short"></span></div>
                                <div class="yap-preview-state-card is-empty" data-yap-state-view="empty" hidden><b>کاتالوگ یا candidate معتبری موجود نیست.</b><p>در حالت empty هیچ شناسه یا امتیاز ساختگی نباید به‌عنوان پیشنهاد واقعی نمایش داده شود.</p></div>
                                <div class="yap-preview-state-card is-error" data-yap-state-view="error" hidden><b>سرویس embedding یا ranking در دسترس نیست.</b><p>نتیجه باید unavailable باشد؛ fallback ساختگی نباید به‌عنوان match واقعی نشان داده شود.</p></div>
                                <div class="yap-preview-state-card is-stale" data-yap-state-view="stale" hidden><b>پیشنهادها بر اساس دادهٔ قدیمی ساخته شده‌اند.</b><p>زمان آخرین embedding و آخرین event باید به اپراتور نمایش داده شود.</p></div>
                                <p class="yap-panel-disclaimer">تمام شناسه‌ها و آمار ساختگی‌اند. این پنل نمونهٔ UX هدف است و اثبات نمی‌کند قابلیت‌های hard filter، diversity یا attribution در سرویس فعلی تکمیل شده‌اند.</p>
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
