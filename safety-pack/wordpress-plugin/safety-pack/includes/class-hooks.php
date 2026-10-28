<?php
namespace SafetyPack;

/**
 * Hooks — قابلیت‌هایی که به‌صورت خودکار روی سایت اعمال می‌شن
 * بدون نیاز به کد نویسی توسط صاحب سایت
 */
class Hooks {

    private static ?Hooks $instance = null;

    public static function get_instance(): Hooks {
        if (self::$instance === null) self::$instance = new self();
        return self::$instance;
    }

    private function __construct() {
        if (!License::is_active()) return;

        // ── Auto-moderate comment ────────────────────────────────────────
        if (get_option('safety_pack_auto_moderate', '1') === '1') {
            add_filter('preprocess_comment', [$this, 'filter_comment'], 10, 1);
        }

        // ── NSFW block on media upload ───────────────────────────────────
        if (get_option('safety_pack_block_nsfw', '1') === '1') {
            add_filter('wp_handle_upload_prefilter', [$this, 'filter_upload'], 10, 1);
        }

        // ── REST API endpoint برای بررسی متن از frontend ────────────────
        add_action('rest_api_init', [$this, 'register_rest_routes']);
    }

    // ── Comment Filter ────────────────────────────────────────────────────
    public function filter_comment(array $comment_data): array {
        $content = $comment_data['comment_content'] ?? '';
        if (empty(trim($content))) return $comment_data;

        $client = ApiClient::get_instance();
        $result = $client->moderate_text($content, 'comment');

        if (!empty($result['error'])) return $comment_data; // fail open

        if (isset($result['allowed']) && $result['allowed'] === false) {
            wp_die(
                'این کامنت توسط سیستم مدیریت محتوا مسدود شد: ' . ($result['reason'] ?? 'محتوای نامناسب'),
                'کامنت مسدود شد',
                ['response' => 403, 'back_link' => true]
            );
        }

        return $comment_data;
    }

    // ── Upload Filter (NSFW) ─────────────────────────────────────────────
    public function filter_upload(array $file): array {
        // فقط تصویر
        if (!str_starts_with($file['type'] ?? '', 'image/')) return $file;

        $tmp_path = $file['tmp_name'] ?? '';
        if (!$tmp_path || !file_exists($tmp_path)) return $file;

        $client = ApiClient::get_instance();
        $result = $client->upload_image($tmp_path);

        if (!empty($result['error'])) return $file; // fail open

        if (($result['status'] ?? '') === 'rejected' && ($result['reason'] ?? '') === 'nsfw_detected') {
            $file['error'] = 'تصویر نامناسب تشخیص داده شد و آپلود نشد.';
        }

        return $file;
    }

    // ── REST API ─────────────────────────────────────────────────────────
    public function register_rest_routes(): void {
        // POST /wp-json/safety-pack/v1/moderate
        register_rest_route('safety-pack/v1', '/moderate', [
            'methods'             => 'POST',
            'callback'            => [$this, 'rest_moderate'],
            'permission_callback' => '__return_true',
            'args'                => [
                'text'    => ['required' => true,  'type' => 'string'],
                'context' => ['required' => false, 'type' => 'string', 'default' => 'message'],
            ],
        ]);
    }

    public function rest_moderate(\WP_REST_Request $request): \WP_REST_Response {
        $client = ApiClient::get_instance();
        $result = $client->moderate_text(
            $request->get_param('text'),
            $request->get_param('context'),
        );
        return new \WP_REST_Response($result, empty($result['error']) ? 200 : 500);
    }
}
