<?php
namespace SafetyPack;

/**
 * API Client — همه درخواست‌ها به Safety Pack Gateway
 * 
 * نکته مهم: ai_verification و ai_image فایل می‌گیرن.
 * WordPress از wp_remote_post برای multipart استفاده می‌کنه،
 * ولی برای فایل‌های بزرگ از cURL مستقیم استفاده می‌کنیم.
 */
class ApiClient {

    private static ?ApiClient $instance = null;
    private string $base_url;
    private string $license_key;

    private function __construct() {
        $this->base_url    = rtrim(get_option('safety_pack_api_url', SAFETY_PACK_API_BASE), '/');
        $this->license_key = get_option('safety_pack_license_key', '');
    }

    public static function get_instance(): ApiClient {
        if (self::$instance === null) self::$instance = new self();
        return self::$instance;
    }

    // ── JSON request ─────────────────────────────────────────────────────
    private function request_json(string $method, string $path, array $body = []): array {
        if (empty($this->license_key)) {
            return ['error' => 'License key تنظیم نشده'];
        }
        $response = wp_remote_request($this->base_url . '/' . ltrim($path, '/'), [
            'method'  => strtoupper($method),
            'timeout' => 30,
            'headers' => [
                'Content-Type'  => 'application/json',
                'X-License-Key' => $this->license_key,
            ],
            'body' => !empty($body) ? wp_json_encode($body) : null,
        ]);
        if (is_wp_error($response)) return ['error' => $response->get_error_message()];
        $code = wp_remote_retrieve_response_code($response);
        $data = json_decode(wp_remote_retrieve_body($response), true) ?? [];
        if ($code >= 400) return ['error' => $data['detail'] ?? "خطای سرور ($code)"];
        return $data;
    }

    // ── Multipart file upload با cURL ────────────────────────────────────
    private function request_multipart(string $path, array $files, array $fields = []): array {
        if (empty($this->license_key)) {
            return ['error' => 'License key تنظیم نشده'];
        }

        $url = $this->base_url . '/' . ltrim($path, '/');

        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_POST           => true,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT        => 60,
            CURLOPT_HTTPHEADER     => [
                'X-License-Key: ' . $this->license_key,
            ],
        ]);

        $post_fields = $fields;
        foreach ($files as $field_name => $file_path) {
            $post_fields[$field_name] = new \CURLFile($file_path);
        }
        curl_setopt($ch, CURLOPT_POSTFIELDS, $post_fields);

        $body = curl_exec($ch);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $err  = curl_error($ch);
        curl_close($ch);

        if ($err) return ['error' => $err];
        $data = json_decode($body, true) ?? [];
        if ($code >= 400) return ['error' => $data['detail'] ?? "خطای سرور ($code)"];
        return $data;
    }

    // ── MODERATION ────────────────────────────────────────────────────────

    /**
     * بررسی یه متن
     * @param string $text    متن
     * @param string $context message|bio|comment
     * @param int    $user_id شناسه کاربر (اختیاری)
     */
    public function moderate_text(string $text, string $context = 'message', int $user_id = 0): array {
        return $this->request_json('POST', '/moderate/text', [
            'text'    => $text,
            'context' => $context,
            'user_id' => $user_id ?: null,
        ]);
    }

    /**
     * بررسی دسته‌ای
     * @param string[] $texts
     */
    public function moderate_batch(array $texts, string $context = 'message'): array {
        return $this->request_json('POST', '/moderate/batch', [
            'texts'   => $texts,
            'context' => $context,
        ]);
    }

    // ── VERIFICATION ──────────────────────────────────────────────────────

    /**
     * تطابق چهره سلفی با عکس پروفایل
     * @param string $selfie_path        مسیر فایل سلفی روی سرور
     * @param string $profile_photo_path مسیر عکس پروفایل
     */
    public function verify_face(string $selfie_path, string $profile_photo_path): array {
        return $this->request_multipart('/verify/face', [
            'selfie'        => $selfie_path,
            'profile_photo' => $profile_photo_path,
        ]);
    }

    // ── IMAGE ─────────────────────────────────────────────────────────────

    /**
     * آپلود و بررسی تصویر (EXIF clean + NSFW check)
     * @param string $file_path مسیر فایل روی سرور
     */
    public function upload_image(string $file_path): array {
        return $this->request_multipart('/image/upload', ['file' => $file_path]);
    }

    /**
     * تحلیل کامل تصویر (quality + face)
     */
    public function analyze_image(string $file_path): array {
        return $this->request_multipart('/image/analyze', ['file' => $file_path]);
    }

    public function license_status(): array {
        return $this->request_json('GET', '/license/validate');
    }

    // ── HEALTH ────────────────────────────────────────────────────────────
    public function health_check(): array {
        $r = wp_remote_get($this->base_url . '/health', [
            'timeout' => 10,
            'headers' => ['X-License-Key' => $this->license_key],
        ]);
        if (is_wp_error($r)) return ['status' => 'error', 'message' => $r->get_error_message()];
        return json_decode(wp_remote_retrieve_body($r), true) ?? ['status' => 'unknown'];
    }
}
