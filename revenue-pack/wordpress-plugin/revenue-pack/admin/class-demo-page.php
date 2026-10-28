<?php
namespace RevenuePack;

class DemoPage {
    private static ?DemoPage $instance = null;

    public static function get_instance(): DemoPage {
        if (self::$instance === null) self::$instance = new self();
        return self::$instance;
    }

    private function __construct() {
        add_action('admin_menu', [$this, 'add_menu']);
        add_action('wp_ajax_rp_demo', [$this, 'ajax_demo']);
    }

    public function add_menu(): void {
        add_submenu_page('revenue-pack-settings', 'دمو زنده', '🔬 دمو زنده',
            'manage_options', 'revenue-pack-demo', [$this, 'render']);
    }

    public function render(): void {
        if (!License::is_active()) {
            echo '<div class="wrap"><div class="notice notice-error"><p>ابتدا License key را وارد کنید.</p></div></div>';
            return;
        }
        ?>
        <div class="wrap" dir="rtl">
            <h1>🔬 دمو زنده — Revenue Pack AI</h1>

            <nav class="nav-tab-wrapper" style="margin-bottom:20px">
                <a class="nav-tab nav-tab-active" data-tab="promotion">🎯 پروموشن</a>
                <a class="nav-tab" data-tab="ltv">💎 پیش‌بینی LTV</a>
                <a class="nav-tab" data-tab="uplift">📈 Uplift</a>
                <a class="nav-tab" data-tab="feedback">💬 فیدبک</a>
            </nav>

            <!-- Tab: Promotion -->
            <div id="tab-promotion" class="rp-tab">
                <div class="card" style="max-width:720px;padding:20px">
                    <h2>🎯 بهترین پروموشن برای کاربر</h2>
                    <p>بر اساس ویژگی‌های کاربر، XGBoost تشخیص می‌ده کدوم پروموشن بیشترین احتمال conversion داره.</p>

                    <table style="width:100%;border-collapse:collapse">
                        <tr>
                            <td style="padding:6px 12px 6px 0;width:200px"><label>User ID:</label></td>
                            <td><input type="number" id="promo-uid" value="123" style="width:100px;direction:ltr"></td>
                        </tr>
                        <tr>
                            <td><label>Engagement (0-1):</label></td>
                            <td><input type="range" id="promo-engagement" min="0" max="1" step="0.1" value="0.7">
                                <span id="promo-engagement-val">0.7</span></td>
                        </tr>
                        <tr>
                            <td><label>Intent Score (0-1):</label></td>
                            <td><input type="range" id="promo-intent" min="0" max="1" step="0.1" value="0.6">
                                <span id="promo-intent-val">0.6</span></td>
                        </tr>
                        <tr>
                            <td><label>City Weight (0-1):</label></td>
                            <td><input type="range" id="promo-city" min="0" max="1" step="0.1" value="0.5">
                                <span id="promo-city-val">0.5</span></td>
                        </tr>
                        <tr>
                            <td><label>پروموشن‌های کاندید:</label></td>
                            <td><input type="text" id="promo-candidates" value="discount_10,free_trial,premium_badge,vip_access"
                                style="width:100%;direction:ltr"></td>
                        </tr>
                    </table>
                    <br>
                    <button class="button button-primary rp-btn" data-service="promotion">🎯 پیش‌بینی بهترین پروموشن</button>
                    <div class="rp-result" id="result-promotion"></div>
                </div>
            </div>

            <!-- Tab: LTV -->
            <div id="tab-ltv" class="rp-tab" style="display:none">
                <div class="card" style="max-width:720px;padding:20px">
                    <h2>💎 پیش‌بینی LTV (ارزش مادام‌العمر کاربر)</h2>
                    <p>GradientBoosting بر اساس ۱۲ فیچر، LTV کاربر رو پیش‌بینی می‌کنه.</p>

                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
                        <?php
                        $fields = [
                            'userId'              => ['User ID',              'number', '123'],
                            'channelType'         => ['Channel Type (0-1)',   'range',  '0.5'],
                            'keywordDifficulty'   => ['Keyword Difficulty',   'range',  '0.5'],
                            'contentLength'       => ['Content Length',       'range',  '0.5'],
                            'timeToConversion'    => ['Days to Conversion',   'number', '30'],
                            'cityWeight'          => ['City Weight',          'range',  '0.5'],
                            'intentScore'         => ['Intent Score',         'range',  '0.5'],
                            'engagementDepth'     => ['Engagement Depth',     'number', '5'],
                            'retentionImpact'     => ['Retention Impact',     'range',  '0.5'],
                            'campaignCost'        => ['Campaign Cost ($)',     'number', '0'],
                            'competitorPressure'  => ['Competitor Pressure',  'range',  '0.3'],
                            'seasonalityFactor'   => ['Seasonality Factor',   'range',  '1.0'],
                            'segmentSize'         => ['Segment Size',         'range',  '0.5'],
                        ];
                        foreach ($fields as $id => [$label, $type, $val]):
                        ?>
                        <div>
                            <label style="font-size:12px;display:block;margin-bottom:4px"><?php echo $label; ?>:</label>
                            <input type="<?php echo $type; ?>" id="ltv-<?php echo $id; ?>"
                                value="<?php echo $val; ?>"
                                <?php if ($type === 'range') echo 'min="0" max="1" step="0.1"'; ?>
                                style="width:<?php echo $type==='number'?'80px':'130px'; ?>;direction:ltr">
                            <?php if ($type === 'range'): ?>
                                <span id="ltv-<?php echo $id; ?>-val"><?php echo $val; ?></span>
                            <?php endif; ?>
                        </div>
                        <?php endforeach; ?>
                    </div>
                    <br>
                    <button class="button button-primary rp-btn" data-service="ltv">💎 محاسبه LTV</button>
                    <div class="rp-result" id="result-ltv"></div>
                </div>
            </div>

            <!-- Tab: Uplift -->
            <div id="tab-uplift" class="rp-tab" style="display:none">
                <div class="card" style="max-width:720px;padding:20px">
                    <h2>📈 Uplift Modeling</h2>
                    <p>می‌فهمیم کدوم کاربران واقعاً از کمپین تأثیر می‌گیرن (نه فقط اون‌هایی که خودشون می‌خریدن).</p>
                    <p style="background:#e8f4fd;padding:10px;border-radius:4px;font-size:13px">
                        ⚠️ مدل باید اول train بشه. اگه train نشده، fallback به avg_uplift می‌کنه.
                    </p>

                    <label><strong>Feature matrix (JSON — هر آرایه یه کاربر):</strong></label>
                    <textarea id="uplift-features" rows="8"
                        style="width:100%;font-family:monospace;font-size:12px;direction:ltr;margin-top:8px">
[
  [0.4, 0.7, 0.6, 0.5, 0.3],
  [0.8, 0.3, 0.2, 0.9, 0.6],
  [0.5, 0.5, 0.5, 0.5, 0.5],
  [0.2, 0.9, 0.8, 0.1, 0.7]
]</textarea>
                    <br><br>
                    <button class="button button-primary rp-btn" data-service="uplift">📈 پیش‌بینی Uplift</button>
                    <div class="rp-result" id="result-uplift"></div>
                </div>
            </div>

            <!-- Tab: Feedback -->
            <div id="tab-feedback" class="rp-tab" style="display:none">
                <div class="card" style="max-width:720px;padding:20px">
                    <h2>💬 فیدبک و پیش‌بینی Conversion</h2>

                    <table style="width:100%;border-collapse:collapse;margin-bottom:16px">
                        <tr>
                            <td style="padding:6px 12px 6px 0;width:180px"><label>User ID:</label></td>
                            <td><input type="number" id="fb-uid" value="456" style="width:80px;direction:ltr"></td>
                        </tr>
                        <tr>
                            <td><label>Feature:</label></td>
                            <td>
                                <select id="fb-feature" style="direction:ltr">
                                    <option value="premium_cta">premium_cta</option>
                                    <option value="discount_banner">discount_banner</option>
                                    <option value="free_trial_offer">free_trial_offer</option>
                                    <option value="match_notification">match_notification</option>
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <td><label>Sentiment:</label></td>
                            <td>
                                <select id="fb-sentiment" style="direction:ltr">
                                    <option value="positive">positive</option>
                                    <option value="neutral">neutral</option>
                                    <option value="negative">negative</option>
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <td><label>Sentiment Score (0-1):</label></td>
                            <td><input type="range" id="fb-score" min="0" max="1" step="0.1" value="0.8">
                                <span id="fb-score-val">0.8</span></td>
                        </tr>
                        <tr>
                            <td><label>Impact Score (0-1):</label></td>
                            <td><input type="range" id="fb-impact" min="0" max="1" step="0.1" value="0.6">
                                <span id="fb-impact-val">0.6</span></td>
                        </tr>
                        <tr>
                            <td><label>Revenue Impact ($):</label></td>
                            <td><input type="number" id="fb-revenue" value="50" style="width:80px;direction:ltr"></td>
                        </tr>
                    </table>

                    <div style="display:flex;gap:12px">
                        <button class="button button-primary rp-btn"   data-service="feedback_train">💾 ثبت فیدبک</button>
                        <button class="button button-secondary rp-btn" data-service="feedback_predict">🔮 پیش‌بینی Conversion</button>
                        <button class="button rp-btn"                  data-service="feedback_metrics">📊 آمار مدل</button>
                    </div>
                    <div class="rp-result" id="result-feedback"></div>
                </div>
            </div>
        </div>

        <style>
        .rp-result {
            margin-top:16px;padding:14px;
            background:#1e1e2e;color:#cdd6f4;
            border-radius:6px;font-family:monospace;
            font-size:13px;direction:ltr;
            display:none;white-space:pre-wrap;
        }
        .rp-result.loading { opacity:.6 }
        </style>

        <script>
        // Tabs
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', function(e) {
                e.preventDefault();
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('nav-tab-active'));
                document.querySelectorAll('.rp-tab').forEach(t => t.style.display = 'none');
                this.classList.add('nav-tab-active');
                document.getElementById('tab-' + this.dataset.tab).style.display = 'block';
            });
        });

        // Range display
        document.querySelectorAll('input[type=range]').forEach(r => {
            r.addEventListener('input', function() {
                const span = document.getElementById(this.id + '-val');
                if (span) span.textContent = this.value;
            });
        });

        const nonce = '<?php echo wp_create_nonce('rp_demo'); ?>';

        function showResult(id, data) {
            const el = document.getElementById('result-' + id);
            el.style.display = 'block';
            el.classList.remove('loading');
            el.textContent = JSON.stringify(data, null, 2);
        }
        function setLoading(id) {
            const el = document.getElementById('result-' + id);
            el.style.display = 'block';
            el.classList.add('loading');
            el.textContent = '⏳ در حال پردازش...';
        }

        document.querySelectorAll('.rp-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const service = this.dataset.service;
                const resultKey = service.startsWith('feedback') ? 'feedback' : service;
                setLoading(resultKey);

                const payload = {service};

                if (service === 'promotion') {
                    payload.user_id = parseInt(document.getElementById('promo-uid').value);
                    payload.features = {
                        engagement:   parseFloat(document.getElementById('promo-engagement').value),
                        intent_score: parseFloat(document.getElementById('promo-intent').value),
                        city_weight:  parseFloat(document.getElementById('promo-city').value),
                    };
                    payload.candidates = document.getElementById('promo-candidates').value.split(',').map(s => s.trim());
                }
                else if (service === 'ltv') {
                    const fields = ['userId','channelType','keywordDifficulty','contentLength',
                        'timeToConversion','cityWeight','intentScore','engagementDepth',
                        'retentionImpact','campaignCost','competitorPressure','seasonalityFactor','segmentSize'];
                    payload.data = {};
                    fields.forEach(f => {
                        const el = document.getElementById('ltv-' + f);
                        payload.data[f] = f === 'userId' ? parseInt(el.value) : parseFloat(el.value);
                    });
                }
                else if (service === 'uplift') {
                    try { payload.features = JSON.parse(document.getElementById('uplift-features').value); }
                    catch(e) { showResult('uplift', {error: 'JSON نامعتبر'}); return; }
                }
                else if (service.startsWith('feedback')) {
                    payload.feedback = {
                        userId:         parseInt(document.getElementById('fb-uid').value),
                        feature:        document.getElementById('fb-feature').value,
                        sentiment:      document.getElementById('fb-sentiment').value,
                        sentimentScore: parseFloat(document.getElementById('fb-score').value),
                        impactScore:    parseFloat(document.getElementById('fb-impact').value),
                        revenueImpact:  parseFloat(document.getElementById('fb-revenue').value),
                        value: {}, metadata: {},
                    };
                }

                fetch(ajaxurl, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: 'action=rp_demo&nonce=' + nonce + '&payload=' + encodeURIComponent(JSON.stringify(payload))
                }).then(r => r.json())
                  .then(d => showResult(resultKey, d))
                  .catch(e => showResult(resultKey, {error: e.message}));
            });
        });
        </script>
        <?php
    }

    public function ajax_demo(): void {
        check_ajax_referer('rp_demo', 'nonce');
        if (!current_user_can('manage_options')) wp_die('Unauthorized');

        $payload = json_decode(stripslashes($_POST['payload'] ?? '{}'), true);
        $service = $payload['service'] ?? '';
        $client  = ApiClient::get_instance();

        $result = match(true) {
            $service === 'promotion' => $client->predict_promotion(
                $payload['user_id'] ?? 1,
                $payload['features'] ?? [],
                $payload['candidates'] ?? [],
            ),
            $service === 'ltv' => $client->predict_ltv($payload['data'] ?? []),
            $service === 'uplift' => $client->predict_uplift($payload['features'] ?? []),
            $service === 'feedback_train' => $client->send_feedback($payload['feedback'] ?? []),
            $service === 'feedback_predict' => $client->predict_conversion($payload['feedback'] ?? []),
            $service === 'feedback_metrics' => $client->get_feedback_metrics(),
            default => ['error' => 'سرویس نامشخص'],
        };

        wp_send_json($result);
    }
}
