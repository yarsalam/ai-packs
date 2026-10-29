<?php
namespace SeoPack;

/**
 * API Client — همه درخواست‌ها به Gateway رو مدیریت می‌کنه
 */
class ApiClient {

    private static ?ApiClient $instance = null;
    private string $base_url;
    private string $license_key;

    private function __construct() {
        $this->base_url    = rtrim(get_option('seo_pack_api_url', SEO_PACK_API_BASE), '/');
        $this->license_key = get_option('seo_pack_license_key', '');
    }

    public static function get_instance(): ApiClient {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    // ── Generic request ───────────────────────────────────────────────────
    private function request(string $method, string $path, array $body = []): array {
        if (empty($this->license_key)) {
            return ['error' => 'License key تنظیم نشده. به تنظیمات پلاگین بروید.'];
        }

        $args = [
            'method'  => strtoupper($method),
            'timeout' => 30,
            'headers' => [
                'Content-Type'  => 'application/json',
                'X-License-Key' => $this->license_key,
            ],
        ];

        if (!empty($body)) {
            $args['body'] = wp_json_encode($body);
        }

        $url      = $this->base_url . '/' . ltrim($path, '/');
        $response = wp_remote_request($url, $args);

        if (is_wp_error($response)) {
            return ['error' => $response->get_error_message()];
        }

        $code = wp_remote_retrieve_response_code($response);
        $data = json_decode(wp_remote_retrieve_body($response), true) ?? [];

        if ($code >= 400) {
            return ['error' => $data['detail'] ?? "خطای سرور ($code)"];
        }

        return $data;
    }

    // ── SEO: Traffic Prediction ───────────────────────────────────────────
    /**
     * @param array $historical_data  آرایه‌ای از ['date'=>'2024-01-01','visits'=>1200]
     * @param int   $days             تعداد روزهای پیش‌بینی (پیش‌فرض ۹۰)
     */
    public function predict_traffic(array $historical_data, int $days = 90): array {
        return $this->request('POST', '/seo/predict/traffic', [
            'historical_data' => $historical_data,
            'days'            => $days,
        ]);
    }

    // ── AEO: Brand Mention Check ──────────────────────────────────────────
    /**
     * @param string   $brand    نام برند
     * @param string[] $prompts  سوال‌هایی که به AI می‌پرسیم
     */
    public function check_aeo_mentions(string $brand, array $prompts): array {
        return $this->request('POST', '/aeo/check-mentions', [
            'brand'   => $brand,
            'prompts' => $prompts,
            'persist' => true,
        ]);
    }

    public function get_aeo_history(string $brand): array {
        return $this->request('GET', "/aeo/history/{$brand}");
    }

    // ── Backlink: Trust Flow ──────────────────────────────────────────────
    /**
     * @param array $edges          [['from.com','to.com'], ...]
     * @param array $trusted_seeds  دامنه‌های مورد اعتماد
     */
    public function analyze_trust_flow(array $edges, array $trusted_seeds = []): array {
        return $this->request('POST', '/backlink/trust-flow', [
            'edges'         => $edges,
            'trusted_seeds' => $trusted_seeds,
        ]);
    }

    public function topic_similarity(string $source_text, string $target_text): array {
        return $this->request('POST', '/backlink/topic-similarity', [
            'source_text' => $source_text,
            'target_text' => $target_text,
        ]);
    }

    // ── Recommender ───────────────────────────────────────────────────────
    public function get_seo_recommendations(string $user_id, int $n = 5): array {
        return $this->request('POST', '/recommend/recommend', [
            'user_id' => $user_id,
            'n'       => $n,
        ]);
    }

    public function license_status(): array {
        return $this->request('GET', '/license/validate');
    }

    // ── Health Check ──────────────────────────────────────────────────────
    public function health_check(): array {
        $args = [
            'timeout' => 10,
            'headers' => ['X-License-Key' => $this->license_key],
        ];
        $response = wp_remote_get($this->base_url . '/health', $args);
        if (is_wp_error($response)) {
            return ['status' => 'error', 'message' => $response->get_error_message()];
        }
        return json_decode(wp_remote_retrieve_body($response), true) ?? ['status' => 'unknown'];
    }
}
