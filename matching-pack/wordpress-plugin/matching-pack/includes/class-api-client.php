<?php
namespace MatchingPack;

class ApiClient {

    private static ?ApiClient $instance = null;
    private string $base_url;
    private string $license_key;

    private function __construct() {
        $this->base_url    = rtrim(get_option('matching_pack_api_url', MATCHING_PACK_API_BASE), '/');
        $this->license_key = get_option('matching_pack_license_key', '');
    }

    public static function get_instance(): ApiClient {
        if (self::$instance === null) self::$instance = new self();
        return self::$instance;
    }

    private function request(string $method, string $path, array $body = [], int $timeout = 60): array {
        if (empty($this->license_key))
            return ['error' => 'License key تنظیم نشده'];

        $args = [
            'method'  => strtoupper($method),
            'timeout' => $timeout,   // NLP مدل‌ها کند هستن
            'headers' => [
                'Content-Type'  => 'application/json',
                'X-License-Key' => $this->license_key,
            ],
        ];
        if (!empty($body)) $args['body'] = wp_json_encode($body);

        $response = wp_remote_request($this->base_url . '/' . ltrim($path, '/'), $args);
        if (is_wp_error($response)) return ['error' => $response->get_error_message()];
        $code = wp_remote_retrieve_response_code($response);
        $data = json_decode(wp_remote_retrieve_body($response), true) ?? [];
        if ($code >= 400) return ['error' => $data['detail'] ?? "خطای سرور ($code)"];
        return $data;
    }

    // ── MATCHING ──────────────────────────────────────────────────────────────

    /** Embed متن کاربر و cache روی Redis */
    public function embed_user(int $user_id, string $text): array {
        return $this->request('POST', '/match/embed', [
            'text'    => $text,
            'user_id' => $user_id,
        ]);
    }

    /** پیشنهاد بهترین کاندیداها برای یه کاربر */
    public function recommend_matches(int $user_id, array $candidate_ids, int $limit = 10): array {
        return $this->request('POST', '/match/recommend', [
            'user_id'    => $user_id,
            'candidates' => $candidate_ids,
            'limit'      => $limit,
        ]);
    }

    /** Match score بین دو کاربر (0-1) */
    public function predict_match_score(int $user_a, int $user_b): array {
        return $this->request('POST', '/match/predict', [
            'user_a' => $user_a,
            'user_b' => $user_b,
        ]);
    }

    /** Track رویداد (like, skip, message) */
    public function track_event(int $user_id, string $type, int $target_id): array {
        return $this->request('POST', '/match/track-events', [
            'user_id' => $user_id,
            'events'  => [['type' => $type, 'target_id' => $target_id,
                           'timestamp' => current_time('c')]],
        ]);
    }

    // ── EMBEDDING ─────────────────────────────────────────────────────────────

    /** Embed یه متن مستقیم */
    public function embed_text(string $text): array {
        return $this->request('POST', '/embed/text', ['text' => $text]);
    }

    /** Similarity بین دو vector */
    public function compute_similarity(array $vec_a, array $vec_b): array {
        return $this->request('POST', '/embed/similarity', [
            'vector_a' => $vec_a,
            'vector_b' => $vec_b,
        ]);
    }

    // ── PERSONALITY ───────────────────────────────────────────────────────────

    /** تحلیل sentiment چند پیام */
    public function analyze_sentiment(array $messages): array {
        return $this->request('POST', '/personality/sentiment', ['messages' => $messages], 90);
    }

    /** تشخیص emotion چند پیام */
    public function analyze_emotion(array $messages): array {
        return $this->request('POST', '/personality/emotion', ['messages' => $messages], 90);
    }

    // ── ASSISTANT ─────────────────────────────────────────────────────────────

    /** آنالیز کامل یه کاربر */
    public function analyze_user(int $user_id, string $bio, array $messages, array $events): array {
        return $this->request('POST', '/assistant/analyze', [
            'user_id'  => $user_id,
            'bio'      => $bio,
            'messages' => $messages,
            'events'   => $events,
        ], 60);
    }

    /** پیشنهادات بهبود پروفایل */
    public function get_advice(int $user_id): array {
        return $this->request('GET', "/assistant/advice/{$user_id}");
    }

    // ── SUPPORT ───────────────────────────────────────────────────────────────

    /** آنالیز تیکت پشتیبانی */
    public function analyze_ticket(int $ticket_id, string $content, int $user_id,
                                   string $user_tier = 'free', int $total_purchases = 0): array {
        return $this->request('POST', '/support/analyze', [
            'ticketId'        => $ticket_id,
            'content'         => $content,
            'userId'          => $user_id,
            'userTier'        => $user_tier,
            'totalPurchases'  => $total_purchases,
        ], 60);
    }

    /** فیدبک بعد از حل تیکت */
    public function send_support_feedback(int $ticket_id, int $rating, string $comment = ''): array {
        return $this->request('POST', '/support/feedback', [
            'ticketId' => $ticket_id,
            'rating'   => $rating,
            'comment'  => $comment,
        ]);
    }

    /** SEO insights از تیکت‌ها */
    public function get_seo_insights(int $days = 30): array {
        return $this->request('GET', "/support/seo-insights?days={$days}");
    }

    // ── HEALTH ────────────────────────────────────────────────────────────────
    public function health_check(): array {
        $r = wp_remote_get($this->base_url . '/health', [
            'timeout' => 15,
            'headers' => ['X-License-Key' => $this->license_key],
        ]);
        if (is_wp_error($r)) return ['status' => 'error', 'message' => $r->get_error_message()];
        return json_decode(wp_remote_retrieve_body($r), true) ?? ['status' => 'unknown'];
    }
}
