<?php
/**
 * Plugin Name: Safety Pack AI
 * Plugin URI:  https://yoursite.com/safety-pack
 * Description: هوش مصنوعی ایمنی محتوا — مدیریت متن، تأیید چهره، و پردازش تصویر
 * Version:     1.0.0
 * Author:      YarSalam AI
 * License:     Commercial
 * Text Domain: safety-pack
 */

defined('ABSPATH') || exit;

define('SAFETY_PACK_VERSION',    '1.0.0');
define('SAFETY_PACK_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('SAFETY_PACK_PLUGIN_URL', plugin_dir_url(__FILE__));
define('SAFETY_PACK_API_BASE',   get_option('safety_pack_api_url', 'https://api.yoursite.com/safety-pack'));

require_once SAFETY_PACK_PLUGIN_DIR . 'includes/class-api-client.php';
require_once SAFETY_PACK_PLUGIN_DIR . 'includes/class-license.php';
require_once SAFETY_PACK_PLUGIN_DIR . 'includes/class-hooks.php';
require_once SAFETY_PACK_PLUGIN_DIR . 'admin/class-settings-page.php';
require_once SAFETY_PACK_PLUGIN_DIR . 'admin/class-demo-page.php';

add_action('plugins_loaded', function () {
    SafetyPack\License::get_instance();
    SafetyPack\Hooks::get_instance();       // ← auto-moderate روی comment/registration
    if (is_admin()) {
        SafetyPack\SettingsPage::get_instance();
        SafetyPack\DemoPage::get_instance();
    }
});

register_activation_hook(__FILE__, function () {
    add_option('safety_pack_license_key',      '');
    add_option('safety_pack_api_url',          'https://api.yoursite.com/safety-pack');
    add_option('safety_pack_auto_moderate',    '1');
    add_option('safety_pack_block_nsfw',       '1');
    add_option('safety_pack_verify_on_upload', '0');
});
