<?php
namespace SafetyPack;

class SettingsPage {
    private static ?SettingsPage $instance = null;

    public static function get_instance(): SettingsPage {
        if (self::$instance === null) self::$instance = new self();
        return self::$instance;
    }

    private function __construct() {
        add_action('admin_menu',  [$this, 'add_menu']);
        add_action('admin_init',  [$this, 'register_settings']);
        add_action('wp_ajax_safety_pack_test', [$this, 'ajax_test']);
    }

    public function add_menu(): void {
        add_menu_page('Safety Pack AI', 'Safety Pack AI', 'manage_options',
            'safety-pack-settings', [$this, 'render'], 'dashicons-shield', 81);
        add_submenu_page('safety-pack-settings', 'تنظیمات', 'تنظیمات',
            'manage_options', 'safety-pack-settings', [$this, 'render']);
    }

    public function register_settings(): void {
        foreach (['safety_pack_license_key', 'safety_pack_api_url',
                  'safety_pack_auto_moderate', 'safety_pack_block_nsfw',
                  'safety_pack_verify_on_upload'] as $opt) {
            register_setting('safety_pack_options', $opt);
        }
    }

    public function render(): void {
        $is_active = License::is_active();
        ?>
        <div class="wrap" dir="rtl">
            <h1>🛡️ تنظیمات Safety Pack AI</h1>

            <?php if ($is_active): ?>
                <div class="notice notice-success inline"><p>✅ اتصال برقرار — سرویس‌ها فعال</p></div>
            <?php else: ?>
                <div class="notice notice-error inline"><p>❌ اتصال برقرار نیست</p></div>
            <?php endif; ?>

            <form method="post" action="options.php">
                <?php settings_fields('safety_pack_options'); ?>
                <table class="form-table">
                    <tr>
                        <th>🔑 License Key</th>
                        <td>
                            <input type="password" name="safety_pack_license_key"
                                value="<?php echo esc_attr(get_option('safety_pack_license_key')); ?>"
                                class="regular-text" placeholder="sk-xxxxxx"/>
                        </td>
                    </tr>
                    <tr>
                        <th>🌐 آدرس API</th>
                        <td>
                            <input type="url" name="safety_pack_api_url"
                                value="<?php echo esc_attr(get_option('safety_pack_api_url', 'https://api.yoursite.com/safety-pack')); ?>"
                                class="regular-text"/>
                        </td>
                    </tr>
                </table>

                <h2>⚙️ قابلیت‌های خودکار</h2>
                <table class="form-table">
                    <tr>
                        <th>فیلتر خودکار کامنت‌ها</th>
                        <td>
                            <label>
                                <input type="checkbox" name="safety_pack_auto_moderate" value="1"
                                    <?php checked(get_option('safety_pack_auto_moderate', '1'), '1'); ?>>
                                بررسی ai_moderation قبل از ثبت هر کامنت
                            </label>
                        </td>
                    </tr>
                    <tr>
                        <th>بلاک تصاویر NSFW</th>
                        <td>
                            <label>
                                <input type="checkbox" name="safety_pack_block_nsfw" value="1"
                                    <?php checked(get_option('safety_pack_block_nsfw', '1'), '1'); ?>>
                                بررسی ai_image قبل از آپلود هر تصویر
                            </label>
                        </td>
                    </tr>
                </table>
                <?php submit_button('ذخیره تنظیمات'); ?>
            </form>

            <hr>
            <h2>🔌 تست اتصال</h2>
            <button id="sp-test-btn" class="button button-secondary">تست همه سرویس‌ها</button>
            <div id="sp-test-result" style="margin-top:12px;padding:12px;background:#1e1e2e;color:#cdd6f4;
                border-radius:6px;font-family:monospace;font-size:13px;direction:ltr;display:none;white-space:pre-wrap"></div>
        </div>

        <script>
        document.getElementById('sp-test-btn').addEventListener('click', function() {
            const btn = this, res = document.getElementById('sp-test-result');
            btn.disabled = true; res.style.display = 'block'; res.textContent = '⏳ در حال بررسی...';
            fetch(ajaxurl, {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'action=safety_pack_test&nonce=<?php echo wp_create_nonce('sp_nonce'); ?>'
            }).then(r => r.json()).then(d => {
                res.textContent = JSON.stringify(d, null, 2);
            }).catch(e => res.textContent = '❌ ' + e.message)
            .finally(() => { btn.disabled = false; });
        });
        </script>
        <?php
    }

    public function ajax_test(): void {
        check_ajax_referer('sp_nonce', 'nonce');
        wp_send_json(ApiClient::get_instance()->health_check());
    }
}
