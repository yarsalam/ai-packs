<?php
namespace SeoPack;

class SettingsPage {

    private static ?SettingsPage $instance = null;

    public static function get_instance(): SettingsPage {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        add_action('admin_menu', [$this, 'add_menu']);
        add_action('admin_init', [$this, 'register_settings']);
        add_action('wp_ajax_seo_pack_test_connection', [$this, 'ajax_test_connection']);
        add_action('wp_ajax_seo_pack_generate_license', [$this, 'ajax_generate_license']);
    }

    public function add_menu(): void {
        add_menu_page(
            'SEO Pack AI',
            'SEO Pack AI',
            'manage_options',
            'seo-pack-settings',
            [$this, 'render_settings'],
            'dashicons-chart-line',
            80
        );
        add_submenu_page(
            'seo-pack-settings',
            'تنظیمات',
            'تنظیمات',
            'manage_options',
            'seo-pack-settings',
            [$this, 'render_settings']
        );
    }

    public function register_settings(): void {
        register_setting('seo_pack_options', 'seo_pack_license_key', [
            'sanitize_callback' => 'sanitize_text_field',
        ]);
        register_setting('seo_pack_options', 'seo_pack_api_url', [
            'sanitize_callback' => 'esc_url_raw',
            'default'           => 'https://api.yoursite.com/seo-pack',
        ]);
    }

    public function render_settings(): void {
        $license_key = get_option('seo_pack_license_key', '');
        $api_url     = get_option('seo_pack_api_url', 'https://api.yoursite.com/seo-pack');
        $is_active   = License::is_active();
        ?>
        <div class="wrap">
            <h1>⚙️ تنظیمات SEO Pack AI</h1>

            <?php if ($is_active): ?>
                <div class="notice notice-success inline"><p>✅ اتصال برقرار است — سرویس‌ها فعال هستند</p></div>
            <?php else: ?>
                <div class="notice notice-error inline"><p>❌ اتصال برقرار نیست — License key رو چک کنید</p></div>
            <?php endif; ?>

            <form method="post" action="options.php">
                <?php settings_fields('seo_pack_options'); ?>
                <table class="form-table">
                    <tr>
                        <th><label for="seo_pack_license_key">🔑 License Key</label></th>
                        <td>
                            <input
                                type="password"
                                id="seo_pack_license_key"
                                name="seo_pack_license_key"
                                value="<?php echo esc_attr($license_key); ?>"
                                class="regular-text"
                                placeholder="sk-xxxxxxxxxxxxxxxxxxxxxx"
                            />
                            <p class="description">License key که بعد از خرید دریافت کردید</p>
                        </td>
                    </tr>
                    <tr>
                        <th><label for="seo_pack_api_url">🌐 آدرس API</label></th>
                        <td>
                            <input
                                type="url"
                                id="seo_pack_api_url"
                                name="seo_pack_api_url"
                                value="<?php echo esc_attr($api_url); ?>"
                                class="regular-text"
                            />
                            <p class="description">آدرس Gateway سرویس‌های SEO</p>
                        </td>
                    </tr>
                </table>
                <?php submit_button('ذخیره تنظیمات'); ?>
            </form>

            <hr>
            <h2>🔌 تست اتصال</h2>
            <button id="seo-pack-test-btn" class="button button-secondary">تست اتصال به سرویس‌ها</button>
            <div id="seo-pack-test-result" style="margin-top:12px;padding:12px;background:#f8f8f8;border-radius:4px;display:none;font-family:monospace;font-size:13px;"></div>

            <hr>
            <h2>📊 وضعیت سرویس‌ها</h2>
            <table class="wp-list-table widefat striped" style="max-width:600px">
                <thead><tr><th>سرویس</th><th>پورت</th><th>عملکرد</th></tr></thead>
                <tbody>
                    <tr><td>AI SEO (پیش‌بینی ترافیک)</td><td>8021</td><td>predict/traffic · feedback/campaign</td></tr>
                    <tr><td>AEO Tracker (دیده‌شدن در AI)</td><td>8030</td><td>check-mentions · history</td></tr>
                    <tr><td>Backlink Quality</td><td>8032</td><td>trust-flow · topic-similarity</td></tr>
                    <tr><td>SEO Recommender</td><td>8033</td><td>recommend · train</td></tr>
                </tbody>
            </table>
        </div>

        <script>
        document.getElementById('seo-pack-test-btn').addEventListener('click', function() {
            const btn = this;
            const result = document.getElementById('seo-pack-test-result');
            btn.disabled = true;
            btn.textContent = 'در حال بررسی...';
            result.style.display = 'block';
            result.textContent = '⏳ در حال اتصال به سرویس‌ها...';

            fetch(ajaxurl, {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'action=seo_pack_test_connection&nonce=<?php echo wp_create_nonce('seo_pack_nonce'); ?>'
            })
            .then(r => r.json())
            .then(data => {
                result.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            })
            .catch(e => { result.textContent = '❌ خطا: ' + e.message; })
            .finally(() => { btn.disabled = false; btn.textContent = 'تست اتصال به سرویس‌ها'; });
        });
        </script>
        <?php
    }

    public function ajax_test_connection(): void {
        check_ajax_referer('seo_pack_nonce', 'nonce');
        if (!current_user_can('manage_options')) wp_die('Unauthorized');
        $client = ApiClient::get_instance();
        wp_send_json($client->health_check());
    }
}
