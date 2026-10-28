<?php
/**
 * Plugin Name: Revenue Pack AI
 * Plugin URI:  https://yoursite.com/revenue-pack
 * Description: هوش مصنوعی درآمد — پیش‌بینی LTV، بهترین پروموشن، uplift modeling، و تحلیل فیدبک
 * Version:     1.0.0
 * Author:      YarSalam AI
 * License:     Commercial
 * Text Domain: revenue-pack
 */

defined('ABSPATH') || exit;

define('REVENUE_PACK_VERSION',    '1.0.0');
define('REVENUE_PACK_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('REVENUE_PACK_PLUGIN_URL', plugin_dir_url(__FILE__));
define('REVENUE_PACK_API_BASE',   get_option('revenue_pack_api_url', 'https://api.yoursite.com/revenue-pack'));

require_once REVENUE_PACK_PLUGIN_DIR . 'includes/class-api-client.php';
require_once REVENUE_PACK_PLUGIN_DIR . 'includes/class-license.php';
require_once REVENUE_PACK_PLUGIN_DIR . 'admin/class-settings-page.php';
require_once REVENUE_PACK_PLUGIN_DIR . 'admin/class-demo-page.php';

add_action('plugins_loaded', function () {
    RevenuePack\License::get_instance();
    if (is_admin()) {
        RevenuePack\SettingsPage::get_instance();
        RevenuePack\DemoPage::get_instance();
    }
});

register_activation_hook(__FILE__, function () {
    add_option('revenue_pack_license_key', '');
    add_option('revenue_pack_api_url', 'https://api.yoursite.com/revenue-pack');
});
