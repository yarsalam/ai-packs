<?php
namespace MatchingPack;

class SettingsPage {
    private static ?SettingsPage $instance = null;

    public static function get_instance(): SettingsPage {
        if (self::$instance === null) self::$instance = new self();
        return self::$instance;
    }

    private function __construct() {
        add_action('admin_menu',  [$this, 'add_menu']);
        add_action('admin_init',  [$this, 'register_settings']);
        add_action('wp_ajax_matching_pack_test', [$this, 'ajax_test']);
    }

    public function add_menu(): void {
        add_menu_page('Matching Pack AI', 'Matching Pack AI', 'manage_options',
            'matching-pack-settings', [$this, 'render'], 'dashicons-networking', 83);
        add_submenu_page('matching-pack-settings', 'تنظیمات', 'تنظیمات',
            'manage_options', 'matching-pack-settings', [$this, 'render']);
    }

    public function register_settings(): void {
        register_setting('matching_pack_options', 'matching_pack_license_key');
        register_setting('matching_pack_options', 'matching_pack_api_url');
    }

    public function render(): void {
        $is_active = License::is_active();
        ?>
        <div class="wrap" dir="rtl">
            <h1>🤝 تنظیمات Matching Pack AI</h1>

            <?php if ($is_active): ?>
                <div class="notice notice-success inline"><p>✅ اتصال برقرار — همه سرویس‌ها فعال</p></div>
            <?php else: ?>
                <div class="notice notice-error inline"><p>❌ اتصال برقرار نیست</p></div>
            <?php endif; ?>

            <form method="post" action="options.php">
                <?php settings_fields('matching_pack_options'); ?>
                <table class="form-table">
                    <tr>
                        <th>🔑 License Key</th>
                        <td><input type="password" name="matching_pack_license_key"
                            value="<?php echo esc_attr(get_option('matching_pack_license_key')); ?>"
                            class="regular-text" placeholder="sk-xxxxxx"/></td>
                    </tr>
                    <tr>
                        <th>🌐 آدرس API</th>
                        <td><input type="url" name="matching_pack_api_url"
                            value="<?php echo esc_attr(get_option('matching_pack_api_url')); ?>"
                            class="regular-text"/></td>
                    </tr>
                </table>
                <?php submit_button('ذخیره تنظیمات'); ?>
            </form>

            <hr>
            <h2>🔌 تست اتصال</h2>
            <button id="mp-test-btn" class="button button-secondary">تست همه سرویس‌ها</button>
            <div id="mp-test-result" style="margin-top:12px;padding:12px;background:#1e1e2e;color:#cdd6f4;
                border-radius:6px;font-family:monospace;font-size:13px;direction:ltr;display:none;white-space:pre-wrap"></div>

            <hr>
            <h2>📋 سرویس‌ها و وابستگی‌ها</h2>
            <table class="wp-list-table widefat striped" style="max-width:780px">
                <thead><tr><th>سرویس</th><th>پورت</th><th>مدل</th><th>وابستگی</th></tr></thead>
                <tbody>
                    <tr><td>ML Service (Matching)</td><td>:8007</td><td>Cosine Similarity</td><td>embedded_ai:8100, Redis</td></tr>
                    <tr><td>Embedded AI</td><td>:8104</td><td>MiniLM-L12 multilingual</td><td>Redis</td></tr>
                    <tr><td>Personality</td><td>:8101</td><td>HuggingFace (محلی)</td><td>volume: /models</td></tr>
                    <tr><td>AI Assistant</td><td>:8022</td><td>Rule + NLP</td><td>Redis</td></tr>
                    <tr><td>AI Support</td><td>:8016</td><td>BERT فارسی</td><td>volume: /app/models</td></tr>
                </tbody>
            </table>

            <div class="notice notice-info inline" style="margin-top:16px;max-width:780px">
                <p>⚠️ <strong>نکته:</strong> سرویس <code>personality</code> اولین بار کند است — مدل lazy-load می‌شود.
                سرویس‌های <code>personality</code> و <code>ai_support</code> به volume با مدل‌های دانلود شده نیاز دارند.</p>
            </div>
        </div>

        <script>
        document.getElementById('mp-test-btn').addEventListener('click', function() {
            const btn = this, res = document.getElementById('mp-test-result');
            btn.disabled = true; res.style.display = 'block'; res.textContent = '⏳ بررسی (ممکن است ۱۰ ثانیه طول بکشد)...';
            fetch(ajaxurl, {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'action=matching_pack_test&nonce=<?php echo wp_create_nonce('mp_nonce'); ?>'
            }).then(r => r.json()).then(d => {
                res.textContent = JSON.stringify(d, null, 2);
            }).catch(e => res.textContent = '❌ ' + e.message)
            .finally(() => btn.disabled = false);
        });
        </script>
        <?php
    }

    public function ajax_test(): void {
        check_ajax_referer('mp_nonce', 'nonce');
        wp_send_json(ApiClient::get_instance()->health_check());
    }
}
