<?php
/**
 * Plugin Name: Matching Pack AI
 * Plugin URI:  https://yoursite.com/matching-pack
 * Description: هوش مصنوعی مچینگ — تطابق کاربران، تحلیل شخصیت، دستیار هوشمند، و پشتیبانی AI
 * Version:     1.0.0
 * Author:      YarSalam AI
 * License:     Commercial
 * Text Domain: matching-pack
 */

defined('ABSPATH') || exit;

define('MATCHING_PACK_VERSION',    '1.0.0');
define('MATCHING_PACK_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('MATCHING_PACK_PLUGIN_URL', plugin_dir_url(__FILE__));
define('MATCHING_PACK_API_BASE',   get_option('matching_pack_api_url', 'https://api.yoursite.com/matching-pack'));

require_once MATCHING_PACK_PLUGIN_DIR . 'includes/class-api-client.php';
require_once MATCHING_PACK_PLUGIN_DIR . 'includes/class-license.php';
require_once MATCHING_PACK_PLUGIN_DIR . 'admin/class-settings-page.php';
require_once MATCHING_PACK_PLUGIN_DIR . 'admin/class-demo-page.php';

add_action('plugins_loaded', function () {
    MatchingPack\License::get_instance();
    if (is_admin()) {
        MatchingPack\SettingsPage::get_instance();
        MatchingPack\DemoPage::get_instance();
    }
});

register_activation_hook(__FILE__, function () {
    add_option('matching_pack_license_key', '');
    add_option('matching_pack_api_url', 'https://api.yoursite.com/matching-pack');
});
