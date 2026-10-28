<?php
namespace SafetyPack;

class License {
    private static ?License $instance = null;

    public static function get_instance(): License {
        if (self::$instance === null) self::$instance = new self();
        return self::$instance;
    }

    private function __construct() {
        add_action('admin_notices', [$this, 'show_notice']);
    }

    public static function is_active(): bool {
        $key = get_option('safety_pack_license_key', '');
        if (empty($key)) return false;
        $cached = get_transient('safety_pack_license_valid');
        if ($cached !== false) return (bool) $cached;
        $result = ApiClient::get_instance()->health_check();
        $valid  = isset($result['status']) && $result['status'] !== 'error';
        set_transient('safety_pack_license_valid', $valid, 6 * HOUR_IN_SECONDS);
        return $valid;
    }

    public function show_notice(): void {
        if (self::is_active()) return;
        echo '<div class="notice notice-warning"><p>';
        echo '🛡️ <strong>Safety Pack AI:</strong> License key تنظیم نشده. ';
        echo '<a href="' . esc_url(admin_url('admin.php?page=safety-pack-settings')) . '">تنظیمات</a>';
        echo '</p></div>';
    }
}
