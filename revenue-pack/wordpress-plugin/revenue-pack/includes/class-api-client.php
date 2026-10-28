<?php
namespace RevenuePack;

class ApiClient {

    private static ?ApiClient $instance = null;
    private string $base_url;
    private string $license_key;

    private function __construct() {
        $this->base_url    = rtrim(get_option('revenue_pack_api_url', REVENUE_PACK_API_BASE), '/');
        $this->license_key = get_option('revenue_pack_license_key', '');
    }

    public static function get_instance(): ApiClient {
        if (self::$instance === null) self::$instance = new self();
        return self::$instance;
    }

    private function request(string $method, string $path, array $body = []): array {
        if (empty($this->license_key))
            return ['error' => 'License key تنظیم نشده'];

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

    // ── MONETIZATION ──────────────────────────────────────────────────────────

    /**
     * بهترین پروموشن برای یه کاربر
     * @param int    $user_id
     * @param array  $features    ['age'=>0.4, 'engagement'=>0.7, ...]
     * @param array  $candidates  ['discount_10', 'free_trial', 'premium_badge']
     */
    public function predict_promotion(int $user_id, array $features, array $candidates): array {
        return $this->request('POST', '/monetization/predict-promotion', [
            'user_id'    => $user_id,
            'features'   => $features,
            'candidates' => $candidates,
            'context'    => [],
        ]);
    }

    /**
     * ارسال نتیجه واقعی (conversion) برای retrain
     * @param int    $user_id
     * @param string $variant   پروموشنی که نشون داده شد
     * @param array  $features
     * @param int    $label     1=تبدیل شد، 0=نشد
     */
    public function send_monetization_feedback(int $user_id, string $variant, array $features, int $label): array {
        return $this->request('POST', '/monetization/feedback', [
            'user_id'  => $user_id,
            'variant'  => $variant,
            'features' => $features,
            'label'    => $label,
        ]);
    }

    // ── REVENUE / LTV ─────────────────────────────────────────────────────────

    /**
     * پیش‌بینی LTV کاربر
     * همه فیلدها 0-1 هستن مگه timeToConversion (روز)، engagementDepth، و campaignCost
     */
    public function predict_ltv(array $params): array {
        return $this->request('POST', '/revenue/predict/ltv', $params);
    }

    // ── UPLIFT ────────────────────────────────────────────────────────────────

    /**
     * پیش‌بینی uplift برای گروهی از کاربران
     * @param array $features_matrix  آرایه دوبعدی [[f1,f2,...], [f1,f2,...]]
     */
    public function predict_uplift(array $features_matrix): array {
        return $this->request('POST', '/uplift/predict', [
            'features' => $features_matrix,
        ]);
    }

    // ── FEEDBACK ──────────────────────────────────────────────────────────────

    /**
     * ثبت فیدبک یه کاربر (incremental — بلافاصله)
     */
    public function send_feedback(array $feedback_data): array {
        return $this->request('POST', '/feedback/train', $feedback_data);
    }

    /**
     * پیش‌بینی احتمال conversion یه کاربر
     */
    public function predict_conversion(array $feedback_data): array {
        return $this->request('POST', '/feedback/predict', $feedback_data);
    }

    /**
     * آمار و وضعیت مدل feedback
     */
    public function get_feedback_metrics(): array {
        return $this->request('GET', '/feedback/metrics');
    }

    // ── HEALTH ────────────────────────────────────────────────────────────────
    public function health_check(): array {
        $r = wp_remote_get($this->base_url . '/health', [
            'timeout' => 10,
            'headers' => ['X-License-Key' => $this->license_key],
        ]);
        if (is_wp_error($r)) return ['status' => 'error', 'message' => $r->get_error_message()];
        return json_decode(wp_remote_retrieve_body($r), true) ?? ['status' => 'unknown'];
    }
}
