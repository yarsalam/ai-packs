<?php
namespace SeoPack;

class License {

    private static ?License $instance = null;

    public static function get_instance(): License {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        add_action('admin_notices', [$this, 'show_notice']);
    }

    public static function is_active(): bool {
        $key = get_option('seo_pack_license_key', '');
        if (empty($key)) return false;

        // Cache نتیجه برای ۶ ساعت
        $cached = get_transient('seo_pack_license_valid');
        if ($cached !== false) return (bool) $cached;

        $client = ApiClient::get_instance();
        $result = $client->health_check();
        $valid  = isset($result['status']) && $result['status'] !== 'error';

        set_transient('seo_pack_license_valid', $valid, 6 * HOUR_IN_SECONDS);
        return $valid;
    }

    public function show_notice(): void {
        if (self::is_active()) return;
        $settings_url = admin_url('admin.php?page=seo-pack-settings');
        echo '<div class="notice notice-warning"><p>';
        echo '🔑 <strong>SEO Pack AI:</strong> ';
        echo 'License key تنظیم نشده یا نامعتبر است. ';
        echo '<a href="' . esc_url($settings_url) . '">تنظیمات</a>';
        echo '</p></div>';
    }
}
