<?php
/**
 * Plugin Name: SEO Pack AI
 * Plugin URI:  https://yoursite.com/seo-pack
 * Description: هوش مصنوعی SEO — پیش‌بینی ترافیک، AEO، بک‌لینک، و پیشنهادات شخصی‌سازی‌شده
 * Version:     1.0.0
 * Author:      YarSalam AI
 * License:     Commercial
 * Text Domain: seo-pack
 */

defined('ABSPATH') || exit;

define('SEO_PACK_VERSION',    '1.0.0');
define('SEO_PACK_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('SEO_PACK_PLUGIN_URL', plugin_dir_url(__FILE__));
define('SEO_PACK_API_BASE',   get_option('seo_pack_api_url', 'https://api.yoursite.com/seo-pack'));

// ── Autoload ──────────────────────────────────────────────────────────────
require_once SEO_PACK_PLUGIN_DIR . 'includes/class-api-client.php';
require_once SEO_PACK_PLUGIN_DIR . 'includes/class-license.php';
require_once SEO_PACK_PLUGIN_DIR . 'admin/class-settings-page.php';
require_once SEO_PACK_PLUGIN_DIR . 'admin/class-demo-page.php';

// ── Bootstrap ─────────────────────────────────────────────────────────────
add_action('plugins_loaded', function () {
    SeoPack\License::get_instance();
    if (is_admin()) {
        SeoPack\SettingsPage::get_instance();
        SeoPack\DemoPage::get_instance();
    }
});

// ── Activation / Deactivation ──────────────────────────────────────────────
register_activation_hook(__FILE__, function () {
    add_option('seo_pack_license_key', '');
    add_option('seo_pack_api_url', 'https://api.yoursite.com/seo-pack');
});

register_deactivation_hook(__FILE__, function () {
    // License رو در سرور غیرفعال کن (اختیاری)
    $license = get_option('seo_pack_license_key');
    if ($license) {
        wp_remote_post(SEO_PACK_API_BASE . '/deactivate', [
            'headers' => ['X-License-Key' => $license],
            'timeout' => 5,
        ]);
    }
});
