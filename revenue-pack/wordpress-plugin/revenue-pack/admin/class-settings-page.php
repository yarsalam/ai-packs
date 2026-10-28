<?php
namespace RevenuePack;

class SettingsPage {
    private static ?SettingsPage $instance = null;

    public static function get_instance(): SettingsPage {
        if (self::$instance === null) self::$instance = new self();
        return self::$instance;
    }

    private function __construct() {
        add_action('admin_menu',  [$this, 'add_menu']);
        add_action('admin_init',  [$this, 'register_settings']);
        add_action('wp_ajax_revenue_pack_test', [$this, 'ajax_test']);
    }

    public function add_menu(): void {
        add_menu_page('Revenue Pack AI', 'Revenue Pack AI', 'manage_options',
            'revenue-pack-settings', [$this, 'render'], 'dashicons-chart-bar', 82);
        add_submenu_page('revenue-pack-settings', 'تنظیمات', 'تنظیمات',
            'manage_options', 'revenue-pack-settings', [$this, 'render']);
    }

    public function register_settings(): void {
        register_setting('revenue_pack_options', 'revenue_pack_license_key');
        register_setting('revenue_pack_options', 'revenue_pack_api_url');
    }

    public function render(): void {
        $is_active = License::is_active();
        ?>
        <div class="wrap" dir="rtl">
            <h1>💰 تنظیمات Revenue Pack AI</h1>

            <?php if ($is_active): ?>
                <div class="notice notice-success inline"><p>✅ اتصال برقرار — همه سرویس‌ها فعال</p></div>
            <?php else: ?>
                <div class="notice notice-error inline"><p>❌ اتصال برقرار نیست</p></div>
            <?php endif; ?>

            <form method="post" action="options.php">
                <?php settings_fields('revenue_pack_options'); ?>
                <table class="form-table">
                    <tr>
                        <th>🔑 License Key</th>
                        <td>
                            <input type="password" name="revenue_pack_license_key"
                                value="<?php echo esc_attr(get_option('revenue_pack_license_key')); ?>"
                                class="regular-text" placeholder="sk-xxxxxx"/>
                        </td>
                    </tr>
                    <tr>
                        <th>🌐 آدرس API</th>
                        <td>
                            <input type="url" name="revenue_pack_api_url"
                                value="<?php echo esc_attr(get_option('revenue_pack_api_url', 'https://api.yoursite.com/revenue-pack')); ?>"
                                class="regular-text"/>
                        </td>
                    </tr>
                </table>
                <?php submit_button('ذخیره تنظیمات'); ?>
            </form>

            <hr>
            <h2>📊 وضعیت سرویس‌ها</h2>
            <button id="rp-test-btn" class="button button-secondary">تست همه سرویس‌ها</button>
            <div id="rp-test-result" style="margin-top:12px;padding:12px;background:#1e1e2e;color:#cdd6f4;
                border-radius:6px;font-family:monospace;font-size:13px;direction:ltr;display:none;white-space:pre-wrap"></div>

            <hr>
            <table class="wp-list-table widefat striped" style="max-width:700px;margin-top:12px">
                <thead><tr><th>سرویس</th><th>پورت</th><th>مدل</th><th>عملکرد</th></tr></thead>
                <tbody>
                    <tr><td>AI Monetization</td><td>:8015</td><td>XGBoost</td><td>انتخاب بهترین پروموشن</td></tr>
                    <tr><td>AI Revenue</td><td>:8006</td><td>GradientBoosting</td><td>پیش‌بینی LTV کاربر</td></tr>
                    <tr><td>AI Uplift</td><td>:8031</td><td>Uplift Tree</td><td>تأثیر واقعی کمپین</td></tr>
                    <tr><td>AI Feedback</td><td>:8005</td><td>GBM + RF</td><td>احتمال conversion</td></tr>
                </tbody>
            </table>
        </div>

        <script>
        document.getElementById('rp-test-btn').addEventListener('click', function() {
            const btn = this, res = document.getElementById('rp-test-result');
            btn.disabled = true; res.style.display = 'block'; res.textContent = '⏳ در حال بررسی...';
            fetch(ajaxurl, {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'action=revenue_pack_test&nonce=<?php echo wp_create_nonce('rp_nonce'); ?>'
            }).then(r => r.json()).then(d => {
                res.textContent = JSON.stringify(d, null, 2);
            }).catch(e => res.textContent = '❌ ' + e.message)
            .finally(() => btn.disabled = false);
        });
        </script>
        <?php
    }

    public function ajax_test(): void {
        check_ajax_referer('rp_nonce', 'nonce');
        wp_send_json(ApiClient::get_instance()->health_check());
    }
}
