<?php
namespace MatchingPack;

class DemoPage {
    private static ?DemoPage $instance = null;

    public static function get_instance(): DemoPage {
        if (self::$instance === null) self::$instance = new self();
        return self::$instance;
    }

    private function __construct() {
        add_action('admin_menu', [$this, 'add_menu']);
        add_action('wp_ajax_mp_demo', [$this, 'ajax_demo']);
    }

    public function add_menu(): void {
        add_submenu_page('matching-pack-settings', 'دمو زنده', '🔬 دمو زنده',
            'manage_options', 'matching-pack-demo', [$this, 'render']);
    }

    public function render(): void {
        if (!License::is_active()) {
            echo '<div class="wrap"><div class="notice notice-error"><p>ابتدا License key را وارد کنید.</p></div></div>';
            return;
        }
        $nonce = wp_create_nonce('mp_demo');
        ?>
        <div class="wrap" dir="rtl">
            <h1>🔬 دمو زنده — Matching Pack AI</h1>

            <nav class="nav-tab-wrapper" style="margin-bottom:20px">
                <a class="nav-tab nav-tab-active" data-tab="match">🤝 مچینگ</a>
                <a class="nav-tab" data-tab="embed">🧠 Embedding</a>
                <a class="nav-tab" data-tab="personality">😊 شخصیت</a>
                <a class="nav-tab" data-tab="assistant">🤖 دستیار</a>
                <a class="nav-tab" data-tab="support">🎫 پشتیبانی</a>
            </nav>

            <!-- Tab: Matching -->
            <div id="tab-match" class="mp-tab">
                <div class="card" style="max-width:720px;padding:20px">
                    <h2>🤝 مچینگ کاربران</h2>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
                        <div>
                            <h3>۱. Embed کاربر</h3>
                            <label>User ID:</label>
                            <input type="number" id="match-embed-uid" value="101" style="width:80px;direction:ltr"><br><br>
                            <label>متن پروفایل:</label>
                            <textarea id="match-embed-text" rows="4" style="width:100%;direction:rtl;margin-top:6px"
                            >علاقه‌مند به کوهنوردی، موسیقی کلاسیک و کتاب‌های فلسفی. دنبال کسی می‌گردم که...</textarea>
                            <button class="button button-primary mp-btn" data-service="embed_user" style="margin-top:8px">📝 ذخیره Embedding</button>
                            <div class="mp-result" id="result-embed_user"></div>
                        </div>
                        <div>
                            <h3>۲. Match Score</h3>
                            <label>User A:</label>
                            <input type="number" id="match-score-a" value="101" style="width:80px;direction:ltr"><br><br>
                            <label>User B:</label>
                            <input type="number" id="match-score-b" value="202" style="width:80px;direction:ltr"><br><br>
                            <p class="description">embedding هر دو باید از قبل ذخیره شده باشه</p>
                            <button class="button button-primary mp-btn" data-service="predict_match" style="margin-top:8px">🎯 محاسبه Match Score</button>
                            <div class="mp-result" id="result-predict_match"></div>
                        </div>
                    </div>
                    <hr>
                    <h3>۳. پیشنهاد بهترین matches</h3>
                    <label>User ID:</label>
                    <input type="number" id="match-rec-uid" value="101" style="width:80px;direction:ltr">
                    <label style="margin-right:12px">Candidates (comma-separated):</label>
                    <input type="text" id="match-rec-candidates" value="202,303,404,505,606" style="width:200px;direction:ltr">
                    <label style="margin-right:12px">Limit:</label>
                    <input type="number" id="match-rec-limit" value="3" style="width:60px;direction:ltr">
                    <br><br>
                    <button class="button button-primary mp-btn" data-service="recommend">🏆 دریافت پیشنهادها</button>
                    <div class="mp-result" id="result-recommend"></div>
                </div>
            </div>

            <!-- Tab: Embedding -->
            <div id="tab-embed" class="mp-tab" style="display:none">
                <div class="card" style="max-width:720px;padding:20px">
                    <h2>🧠 Embedding و Similarity</h2>
                    <p>مدل <strong>paraphrase-multilingual-MiniLM-L12-v2</strong> — فارسی، انگلیسی و ۵۰+ زبان دیگه.</p>

                    <label><strong>متن اول:</strong></label>
                    <textarea id="embed-text-a" rows="3" style="width:100%;direction:rtl;margin:6px 0">علاقه‌مند به ورزش و طبیعت‌گردی هستم</textarea>
                    <label><strong>متن دوم:</strong></label>
                    <textarea id="embed-text-b" rows="3" style="width:100%;direction:rtl;margin:6px 0">کوهنوردی و دوچرخه‌سواری را دوست دارم</textarea>
                    <br>
                    <div style="display:flex;gap:12px">
                        <button class="button button-primary mp-btn" data-service="similarity">📐 محاسبه Similarity</button>
                        <button class="button button-secondary mp-btn" data-service="embed_text">🔢 فقط Embed متن اول</button>
                    </div>
                    <div class="mp-result" id="result-similarity"></div>
                    <div class="mp-result" id="result-embed_text"></div>
                </div>
            </div>

            <!-- Tab: Personality -->
            <div id="tab-personality" class="mp-tab" style="display:none">
                <div class="card" style="max-width:720px;padding:20px">
                    <h2>😊 تحلیل شخصیت و احساسات</h2>
                    <p class="description">⚠️ اولین call کند است — مدل در حین اجرا load می‌شود (۱۰-۳۰ ثانیه)</p>

                    <label><strong>پیام‌ها (هر خط یک پیام):</strong></label>
                    <textarea id="personality-msgs" rows="6" style="width:100%;direction:rtl;margin:8px 0">امروز خیلی خوشحالم!
دلم تنگ شده
خیلی خسته‌ام از همه چیز
عاشق این آهنگ شدم
نمی‌دونم چی بگم</textarea>
                    <br>
                    <div style="display:flex;gap:12px">
                        <button class="button button-primary mp-btn" data-service="sentiment">😄 تحلیل Sentiment</button>
                        <button class="button button-secondary mp-btn" data-service="emotion">💭 تشخیص Emotion</button>
                    </div>
                    <div class="mp-result" id="result-sentiment"></div>
                    <div class="mp-result" id="result-emotion"></div>
                </div>
            </div>

            <!-- Tab: Assistant -->
            <div id="tab-assistant" class="mp-tab" style="display:none">
                <div class="card" style="max-width:720px;padding:20px">
                    <h2>🤖 دستیار هوشمند کاربر</h2>
                    <table style="width:100%;border-collapse:collapse;margin-bottom:16px">
                        <tr>
                            <td style="padding:6px 12px 6px 0;width:120px"><label>User ID:</label></td>
                            <td><input type="number" id="asst-uid" value="123" style="width:80px;direction:ltr"></td>
                        </tr>
                        <tr>
                            <td><label>Bio:</label></td>
                            <td><textarea id="asst-bio" rows="2" style="width:100%;direction:rtl"
                                >دانشجوی مهندسی نرم‌افزار، علاقه‌مند به موسیقی و سفر</textarea></td>
                        </tr>
                        <tr>
                            <td><label>Messages:</label></td>
                            <td><textarea id="asst-msgs" rows="3" style="width:100%;direction:rtl"
                                >سلام خوش اومدی&#10;چه سرگرمی‌هایی داری؟&#10;من هم عاشق موسیقی‌ام</textarea></td>
                        </tr>
                    </table>
                    <div style="display:flex;gap:12px">
                        <button class="button button-primary mp-btn" data-service="analyze_user">🔍 آنالیز کاربر</button>
                        <button class="button button-secondary mp-btn" data-service="get_advice">💡 دریافت توصیه‌ها</button>
                    </div>
                    <div class="mp-result" id="result-analyze_user"></div>
                    <div class="mp-result" id="result-get_advice"></div>
                </div>
            </div>

            <!-- Tab: Support -->
            <div id="tab-support" class="mp-tab" style="display:none">
                <div class="card" style="max-width:720px;padding:20px">
                    <h2>🎫 پشتیبانی هوشمند</h2>
                    <p>تیکت کاربر رو آنالیز می‌کنه و دسته‌بندی، اولویت و پاسخ پیشنهادی می‌ده.</p>
                    <table style="width:100%;border-collapse:collapse;margin-bottom:16px">
                        <tr>
                            <td style="padding:6px 12px 6px 0;width:150px"><label>Ticket ID:</label></td>
                            <td><input type="number" id="sup-ticket" value="1001" style="width:80px;direction:ltr"></td>
                        </tr>
                        <tr>
                            <td><label>User ID:</label></td>
                            <td><input type="number" id="sup-uid" value="123" style="width:80px;direction:ltr"></td>
                        </tr>
                        <tr>
                            <td><label>User Tier:</label></td>
                            <td>
                                <select id="sup-tier" style="direction:ltr">
                                    <option value="free">free</option>
                                    <option value="premium">premium</option>
                                    <option value="vip">vip</option>
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <td><label>محتوای تیکت:</label></td>
                            <td><textarea id="sup-content" rows="4" style="width:100%;direction:rtl;margin-top:6px"
                                >نمیتونم وارد حسابم بشم. رمزم رو فراموش کردم و پیام تأیید نمیاد.</textarea></td>
                        </tr>
                    </table>
                    <div style="display:flex;gap:12px">
                        <button class="button button-primary mp-btn" data-service="analyze_ticket">🔍 آنالیز تیکت</button>
                        <button class="button button-secondary mp-btn" data-service="seo_insights">📊 SEO Insights</button>
                    </div>
                    <div class="mp-result" id="result-analyze_ticket"></div>
                    <div class="mp-result" id="result-seo_insights"></div>
                </div>
            </div>
        </div>

        <style>
        .mp-result {
            margin-top:12px; padding:14px;
            background:#1e1e2e; color:#cdd6f4;
            border-radius:6px; font-family:monospace;
            font-size:12px; direction:ltr;
            display:none; white-space:pre-wrap; max-height:400px; overflow:auto;
        }
        .mp-result.loading { opacity:.6 }
        </style>

        <script>
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', function(e) {
                e.preventDefault();
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('nav-tab-active'));
                document.querySelectorAll('.mp-tab').forEach(t => t.style.display = 'none');
                this.classList.add('nav-tab-active');
                document.getElementById('tab-' + this.dataset.tab).style.display = 'block';
            });
        });

        const nonce = '<?php echo $nonce; ?>';

        function showResult(id, data) {
            const el = document.getElementById('result-' + id);
            el.style.display = 'block';
            el.classList.remove('loading');
            el.textContent = JSON.stringify(data, null, 2);
        }
        function setLoading(id, msg) {
            const el = document.getElementById('result-' + id);
            el.style.display = 'block';
            el.classList.add('loading');
            el.textContent = msg || '⏳ در حال پردازش...';
        }

        document.querySelectorAll('.mp-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const svc = this.dataset.service;
                setLoading(svc, svc.includes('personality') || svc.includes('sentiment') || svc.includes('emotion')
                    ? '⏳ بارگذاری مدل (اولین بار ممکن است ۳۰ ثانیه طول بکشد)...'
                    : '⏳ در حال پردازش...');

                const p = {service: svc};

                if (svc === 'embed_user') {
                    p.user_id = parseInt(document.getElementById('match-embed-uid').value);
                    p.text    = document.getElementById('match-embed-text').value;
                } else if (svc === 'predict_match') {
                    p.user_a = parseInt(document.getElementById('match-score-a').value);
                    p.user_b = parseInt(document.getElementById('match-score-b').value);
                } else if (svc === 'recommend') {
                    p.user_id    = parseInt(document.getElementById('match-rec-uid').value);
                    p.candidates = document.getElementById('match-rec-candidates').value.split(',').map(Number);
                    p.limit      = parseInt(document.getElementById('match-rec-limit').value);
                } else if (svc === 'similarity') {
                    p.text_a = document.getElementById('embed-text-a').value;
                    p.text_b = document.getElementById('embed-text-b').value;
                } else if (svc === 'embed_text') {
                    p.text = document.getElementById('embed-text-a').value;
                } else if (svc === 'sentiment' || svc === 'emotion') {
                    p.messages = document.getElementById('personality-msgs').value.split('\n').filter(Boolean);
                } else if (svc === 'analyze_user') {
                    p.user_id  = parseInt(document.getElementById('asst-uid').value);
                    p.bio      = document.getElementById('asst-bio').value;
                    p.messages = document.getElementById('asst-msgs').value.split('\n').filter(Boolean);
                    p.events   = [];
                } else if (svc === 'get_advice') {
                    p.user_id = parseInt(document.getElementById('asst-uid').value);
                } else if (svc === 'analyze_ticket') {
                    p.ticket_id  = parseInt(document.getElementById('sup-ticket').value);
                    p.user_id    = parseInt(document.getElementById('sup-uid').value);
                    p.user_tier  = document.getElementById('sup-tier').value;
                    p.content    = document.getElementById('sup-content').value;
                } else if (svc === 'seo_insights') {
                    p.days = 30;
                }

                fetch(ajaxurl, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: 'action=mp_demo&nonce=' + nonce + '&payload=' + encodeURIComponent(JSON.stringify(p))
                }).then(r => r.json())
                  .then(d => showResult(svc, d))
                  .catch(e => showResult(svc, {error: e.message}));
            });
        });
        </script>
        <?php
    }

    public function ajax_demo(): void {
        check_ajax_referer('mp_demo', 'nonce');
        if (!current_user_can('manage_options')) wp_die('Unauthorized');

        $p      = json_decode(stripslashes($_POST['payload'] ?? '{}'), true);
        $svc    = $p['service'] ?? '';
        $client = ApiClient::get_instance();

        $result = match($svc) {
            'embed_user'      => $client->embed_user($p['user_id'], $p['text']),
            'predict_match'   => $client->predict_match_score($p['user_a'], $p['user_b']),
            'recommend'       => $client->recommend_matches($p['user_id'], $p['candidates'], $p['limit'] ?? 10),
            'embed_text'      => $client->embed_text($p['text']),
            'similarity'      => $this->_similarity($client, $p),
            'sentiment'       => $client->analyze_sentiment($p['messages']),
            'emotion'         => $client->analyze_emotion($p['messages']),
            'analyze_user'    => $client->analyze_user($p['user_id'], $p['bio'], $p['messages'], $p['events'] ?? []),
            'get_advice'      => $client->get_advice($p['user_id']),
            'analyze_ticket'  => $client->analyze_ticket($p['ticket_id'], $p['content'], $p['user_id'], $p['user_tier'] ?? 'free'),
            'seo_insights'    => $client->get_seo_insights($p['days'] ?? 30),
            default           => ['error' => 'سرویس نامشخص'],
        };

        wp_send_json($result);
    }

    private function _similarity(ApiClient $client, array $p): array {
        // embed هر دو متن، بعد similarity محاسبه کن
        $a = $client->embed_text($p['text_a'] ?? '');
        $b = $client->embed_text($p['text_b'] ?? '');
        if (!empty($a['error'])) return $a;
        if (!empty($b['error'])) return $b;
        $sim = $client->compute_similarity($a['embedding'], $b['embedding']);
        return array_merge($sim, [
            'text_a'     => substr($p['text_a'], 0, 60) . '...',
            'text_b'     => substr($p['text_b'], 0, 60) . '...',
            'dimension'  => $a['dimension'] ?? null,
        ]);
    }
}
