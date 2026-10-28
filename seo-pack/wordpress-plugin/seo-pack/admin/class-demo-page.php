<?php
namespace SeoPack;

/**
 * Demo Page — صفحه پریویو زنده برای هر ۴ سرویس
 * کاربر می‌تونه مستقیماً امتحان کنه بدون کد نوشتن
 */
class DemoPage {

    private static ?DemoPage $instance = null;

    public static function get_instance(): DemoPage {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        add_action('admin_menu',          [$this, 'add_menu']);
        add_action('wp_ajax_seo_pack_demo_call', [$this, 'ajax_demo_call']);
    }

    public function add_menu(): void {
        add_submenu_page(
            'seo-pack-settings',
            'دمو زنده',
            '🔬 دمو زنده',
            'manage_options',
            'seo-pack-demo',
            [$this, 'render_demo']
        );
    }

    public function render_demo(): void {
        if (!License::is_active()) {
            echo '<div class="wrap"><div class="notice notice-error"><p>ابتدا License key را در <a href="' . admin_url('admin.php?page=seo-pack-settings') . '">تنظیمات</a> وارد کنید.</p></div></div>';
            return;
        }
        ?>
        <div class="wrap" dir="rtl">
            <h1>🔬 دمو زنده — SEO Pack AI</h1>
            <p style="color:#666">هر سرویس رو مستقیم اینجا امتحان کنید</p>

            <!-- Tabs -->
            <nav class="nav-tab-wrapper" style="margin-bottom:20px">
                <a href="#tab-traffic"    class="nav-tab nav-tab-active" data-tab="traffic">📈 پیش‌بینی ترافیک</a>
                <a href="#tab-aeo"        class="nav-tab"                data-tab="aeo">🤖 AEO Tracker</a>
                <a href="#tab-backlink"   class="nav-tab"                data-tab="backlink">🔗 کیفیت بک‌لینک</a>
                <a href="#tab-recommend"  class="nav-tab"                data-tab="recommend">💡 پیشنهادات SEO</a>
            </nav>

            <!-- Tab: Traffic Prediction -->
            <div id="tab-traffic" class="seo-pack-tab">
                <div class="card" style="max-width:700px;padding:20px">
                    <h2>📈 پیش‌بینی ترافیک</h2>
                    <p>داده‌های تاریخی بازدید سایت رو وارد کنید تا ترافیک آینده پیش‌بینی بشه.</p>
                    <label><strong>تعداد روزهای پیش‌بینی:</strong></label>
                    <input type="number" id="traffic-days" value="30" min="7" max="365" style="width:80px;margin:0 8px">
                    <br><br>
                    <label><strong>داده‌های تاریخی (JSON):</strong></label>
                    <textarea id="traffic-data" rows="8" style="width:100%;font-family:monospace;font-size:12px;direction:ltr">[
  {"date": "2025-01-01", "visits": 1200},
  {"date": "2025-01-02", "visits": 1350},
  {"date": "2025-01-03", "visits": 980},
  {"date": "2025-01-04", "visits": 1500},
  {"date": "2025-01-05", "visits": 1100},
  {"date": "2025-01-06", "visits": 900},
  {"date": "2025-01-07", "visits": 1400},
  {"date": "2025-01-08", "visits": 1600},
  {"date": "2025-01-09", "visits": 1250},
  {"date": "2025-01-10", "visits": 1700},
  {"date": "2025-01-11", "visits": 1300},
  {"date": "2025-01-12", "visits": 1450},
  {"date": "2025-01-13", "visits": 1800},
  {"date": "2025-01-14", "visits": 2000}
]</textarea>
                    <br>
                    <button class="button button-primary seo-demo-btn" data-service="traffic">🚀 پیش‌بینی کن</button>
                    <div class="seo-demo-result" id="result-traffic"></div>
                </div>
            </div>

            <!-- Tab: AEO -->
            <div id="tab-aeo" class="seo-pack-tab" style="display:none">
                <div class="card" style="max-width:700px;padding:20px">
                    <h2>🤖 AEO Tracker — دیده‌شدن برند در AI</h2>
                    <p>ببینید وقتی کاربران از ChatGPT/Gemini می‌پرسن، برند شما ذکر می‌شه یا نه.</p>
                    <label><strong>نام برند:</strong></label>
                    <input type="text" id="aeo-brand" value="یارسلام" style="width:200px;margin:0 8px">
                    <br><br>
                    <label><strong>سوال‌هایی که به AI می‌پرسیم (هر خط یه سوال):</strong></label>
                    <textarea id="aeo-prompts" rows="5" style="width:100%;direction:rtl">بهترین سایت همسریابی ایرانی کدام است؟
برای ازدواج در ایران کجا ثبت‌نام کنم؟
سایت‌های معتبر دوست‌یابی ایرانی را معرفی کنید</textarea>
                    <br>
                    <button class="button button-primary seo-demo-btn" data-service="aeo">🔍 بررسی کن</button>
                    <div class="seo-demo-result" id="result-aeo"></div>
                </div>
            </div>

            <!-- Tab: Backlink -->
            <div id="tab-backlink" class="seo-pack-tab" style="display:none">
                <div class="card" style="max-width:700px;padding:20px">
                    <h2>🔗 کیفیت بک‌لینک</h2>
                    <p>Trust Flow شبکه لینک‌های سایتتون رو محاسبه کنید.</p>
                    <label><strong>شبکه لینک‌ها (JSON):</strong></label>
                    <textarea id="backlink-edges" rows="6" style="width:100%;font-family:monospace;font-size:12px;direction:ltr">[
  ["google.com", "example.com"],
  ["wikipedia.org", "example.com"],
  ["example.com", "blog.example.com"],
  ["spamsite.xyz", "example.com"]
]</textarea>
                    <br>
                    <label><strong>سایت‌های مورد اعتماد (هر خط یکی):</strong></label>
                    <textarea id="backlink-seeds" rows="3" style="width:100%;font-family:monospace;font-size:12px;direction:ltr">google.com
wikipedia.org</textarea>
                    <br>
                    <button class="button button-primary seo-demo-btn" data-service="backlink">📊 محاسبه Trust Flow</button>
                    <div class="seo-demo-result" id="result-backlink"></div>
                </div>
            </div>

            <!-- Tab: Recommend -->
            <div id="tab-recommend" class="seo-pack-tab" style="display:none">
                <div class="card" style="max-width:700px;padding:20px">
                    <h2>💡 پیشنهادات SEO شخصی‌سازی‌شده</h2>
                    <p>بر اساس رفتار کاربر، کلمات کلیدی پیشنهادی دریافت کنید.</p>
                    <label><strong>User ID:</strong></label>
                    <input type="text" id="recommend-user" value="user_123" style="width:200px;margin:0 8px;direction:ltr">
                    <br><br>
                    <label><strong>تعداد پیشنهادات:</strong></label>
                    <input type="number" id="recommend-n" value="5" min="1" max="20" style="width:60px;margin:0 8px">
                    <br><br>
                    <p class="description">⚠️ مدل باید اول با داده‌های interaction آموزش دیده باشه</p>
                    <button class="button button-primary seo-demo-btn" data-service="recommend">💡 دریافت پیشنهادات</button>
                    <div class="seo-demo-result" id="result-recommend"></div>
                </div>
            </div>
        </div>

        <style>
        .seo-demo-result {
            margin-top: 16px;
            padding: 12px;
            background: #1e1e2e;
            color: #cdd6f4;
            border-radius: 6px;
            font-family: monospace;
            font-size: 13px;
            direction: ltr;
            min-height: 60px;
            display: none;
            white-space: pre-wrap;
        }
        .seo-demo-result.loading { opacity: 0.6; }
        </style>

        <script>
        // Tab switching
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', function(e) {
                e.preventDefault();
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('nav-tab-active'));
                document.querySelectorAll('.seo-pack-tab').forEach(t => t.style.display = 'none');
                this.classList.add('nav-tab-active');
                document.getElementById('tab-' + this.dataset.tab).style.display = 'block';
            });
        });

        // Demo calls
        document.querySelectorAll('.seo-demo-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const service = this.dataset.service;
                const resultEl = document.getElementById('result-' + service);
                resultEl.style.display = 'block';
                resultEl.classList.add('loading');
                resultEl.textContent = '⏳ در حال پردازش...';

                let payload = { service };

                if (service === 'traffic') {
                    try { payload.historical_data = JSON.parse(document.getElementById('traffic-data').value); }
                    catch(e) { resultEl.textContent = '❌ JSON نامعتبر'; return; }
                    payload.days = parseInt(document.getElementById('traffic-days').value);
                }
                else if (service === 'aeo') {
                    payload.brand   = document.getElementById('aeo-brand').value;
                    payload.prompts = document.getElementById('aeo-prompts').value.split('\n').filter(Boolean);
                }
                else if (service === 'backlink') {
                    try { payload.edges = JSON.parse(document.getElementById('backlink-edges').value); }
                    catch(e) { resultEl.textContent = '❌ JSON نامعتبر'; return; }
                    payload.trusted_seeds = document.getElementById('backlink-seeds').value.split('\n').filter(Boolean);
                }
                else if (service === 'recommend') {
                    payload.user_id = document.getElementById('recommend-user').value;
                    payload.n       = parseInt(document.getElementById('recommend-n').value);
                }

                fetch(ajaxurl, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: 'action=seo_pack_demo_call&nonce=<?php echo wp_create_nonce('seo_pack_demo'); ?>&payload=' + encodeURIComponent(JSON.stringify(payload))
                })
                .then(r => r.json())
                .then(data => {
                    resultEl.textContent = JSON.stringify(data, null, 2);
                })
                .catch(e => { resultEl.textContent = '❌ ' + e.message; })
                .finally(() => resultEl.classList.remove('loading'));
            });
        });
        </script>
        <?php
    }

    public function ajax_demo_call(): void {
        check_ajax_referer('seo_pack_demo', 'nonce');
        if (!current_user_can('manage_options')) wp_die('Unauthorized');

        $payload = json_decode(stripslashes($_POST['payload'] ?? '{}'), true);
        $service = $payload['service'] ?? '';
        $client  = ApiClient::get_instance();

        $result = match($service) {
            'traffic'   => $client->predict_traffic($payload['historical_data'] ?? [], $payload['days'] ?? 90),
            'aeo'       => $client->check_aeo_mentions($payload['brand'] ?? '', $payload['prompts'] ?? []),
            'backlink'  => $client->analyze_trust_flow($payload['edges'] ?? [], $payload['trusted_seeds'] ?? []),
            'recommend' => $client->get_seo_recommendations($payload['user_id'] ?? '', $payload['n'] ?? 5),
            default     => ['error' => 'سرویس نامشخص'],
        };

        wp_send_json($result);
    }
}
