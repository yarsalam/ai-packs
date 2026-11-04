<?php
namespace MatchingPack;

class SettingsPage {
    private static ?SettingsPage $instance = null;

    public static function get_instance(): SettingsPage {
        if (self::$instance === null) self::$instance = new self();
        return self::$instance;
    }

    private function __construct() {
        add_action('admin_menu',  [$this, 'add_menu']);
        add_action('admin_init',  [$this, 'register_settings']);
        add_action('wp_ajax_matching_pack_test', [$this, 'ajax_test']);
        add_action('wp_ajax_matching_pack_usage', [$this, 'ajax_usage']);
    }

    public function add_menu(): void {
        add_menu_page('Matching Pack AI', 'Matching Pack AI', 'manage_options',
            'matching-pack-settings', [$this, 'render'], 'dashicons-networking', 83);
        add_submenu_page('matching-pack-settings', 'تنظیمات', 'تنظیمات',
            'manage_options', 'matching-pack-settings', [$this, 'render']);
    }

    public function register_settings(): void {
        register_setting('matching_pack_options', 'matching_pack_license_key');
        register_setting('matching_pack_options', 'matching_pack_api_url');
    }

    public function render(): void {
        $is_active = License::is_active();
        ?>
        <div class="wrap" dir="rtl">
            <h1>🤝 تنظیمات Matching Pack AI</h1>

            <?php if ($is_active): ?>
                <div class="notice notice-success inline"><p>✅ اتصال برقرار — همه سرویس‌ها فعال</p></div>
            <?php else: ?>
                <div class="notice notice-error inline"><p>❌ اتصال برقرار نیست</p></div>
            <?php endif; ?>

            <form method="post" action="options.php">
                <?php settings_fields('matching_pack_options'); ?>
                <table class="form-table">
                    <tr>
                        <th>🔑 License Key</th>
                        <td><input type="password" name="matching_pack_license_key"
                            value="<?php echo esc_attr(get_option('matching_pack_license_key')); ?>"
                            class="regular-text" placeholder="sk-xxxxxx"/></td>
                    </tr>
                    <tr>
                        <th>🌐 آدرس API</th>
                        <td><input type="url" name="matching_pack_api_url"
                            value="<?php echo esc_attr(get_option('matching_pack_api_url')); ?>"
                            class="regular-text"/></td>
                    </tr>
                </table>
                <?php submit_button('ذخیره تنظیمات'); ?>
            </form>

            <hr>
            <h2>🔌 تست اتصال</h2>
            <button id="mp-test-btn" class="button button-secondary">تست همه سرویس‌ها</button>
            <div id="mp-test-result" style="margin-top:12px;padding:12px;background:#1e1e2e;color:#cdd6f4;
                border-radius:6px;font-family:monospace;font-size:13px;direction:ltr;display:none;white-space:pre-wrap"></div>

            <hr>
            <h2>📊 مصرف و سهمیه</h2>
            <p>مصرف واقعی اعتبارهای Gateway و سقف دوره‌های ساعتی و ماهانه را مشاهده کنید.</p>
            <button type="button" id="mp-usage-btn" class="button button-secondary">به‌روزرسانی مصرف</button>
            <div id="mp-usage-result" role="status" aria-live="polite"
                 style="margin-top:12px;max-width:760px;padding:12px;background:#f8f8f8;border-radius:6px">
                برای مشاهده آخرین مصرف و سهمیه، دکمه را انتخاب کنید.
            </div>
            <script>
            (function () {
                const button = document.getElementById('mp-usage-btn');
                const output = document.getElementById('mp-usage-result');
                if (!button || !output) return;
                const nonce = '<?php echo esc_js(wp_create_nonce('mp_nonce')); ?>';
                button.addEventListener('click', async function () {
                    button.disabled = true;
                    button.textContent = 'در حال دریافت...';
                    output.textContent = 'در حال دریافت اطلاعات مصرف از Gateway...';
                    try {
                        const body = new URLSearchParams({action: 'matching_pack_usage', nonce: nonce});
                        const response = await fetch(ajaxurl, {
                            method: 'POST',
                            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                            body: body.toString()
                        });
                        const result = await response.json();
                        if (!response.ok || !result.success) {
                            throw new Error((result.data && result.data.message) || 'دریافت مصرف ناموفق بود');
                        }
                        const data = result.data || {};
                        if (!data.hourly || !data.monthly) {
                            throw new Error('ساختار پاسخ سهمیه معتبر نیست');
                        }
                        output.replaceChildren();
                        const summary = document.createElement('p');
                        summary.textContent = 'پلن: ' + String(data.plan || 'نامشخص') +
                            ' · واحد مصرف: ' + String(data.usage_unit || 'credits');
                        output.appendChild(summary);

                        const table = document.createElement('table');
                        table.className = 'widefat striped';
                        const header = document.createElement('tr');
                        ['دوره', 'مصرف‌شده', 'سقف', 'باقی‌مانده', 'درصد مصرف', 'نوار مصرف'].forEach(function (label) {
                            const cell = document.createElement('th');
                            cell.textContent = label;
                            header.appendChild(cell);
                        });
                        const thead = document.createElement('thead');
                        thead.appendChild(header);
                        table.appendChild(thead);
                        const tbody = document.createElement('tbody');
                        [
                            ['ساعتی', data.hourly],
                            ['ماهانه (' + String(data.monthly.period || 'جاری') + ')', data.monthly]
                        ].forEach(function (entry) {
                            const period = entry[1] || {};
                            const used = Number(period.used || 0);
                            const limit = Number(period.limit || 0);
                            const remaining = Number(period.remaining || 0);
                            const percent = limit > 0 ? Math.min(100, Math.round((used / limit) * 100)) : 0;
                            const row = document.createElement('tr');
                            [entry[0], String(used), String(limit), String(remaining), percent + '%'].forEach(function (value) {
                                const cell = document.createElement('td');
                                cell.textContent = value;
                                row.appendChild(cell);
                            });
                            const progressCell = document.createElement('td');
                            const progress = document.createElement('progress');
                            progress.max = limit > 0 ? limit : 1;
                            progress.value = limit > 0 ? Math.min(used, limit) : 0;
                            progress.setAttribute('aria-label', entry[0] + ' usage ' + percent + '%');
                            progressCell.appendChild(progress);
                            row.appendChild(progressCell);
                            tbody.appendChild(row);
                        });
                        table.appendChild(tbody);
                        output.appendChild(table);
                        const updated = document.createElement('p');
                        updated.textContent = 'آخرین به‌روزرسانی: ' + new Date().toLocaleString();
                        output.appendChild(updated);
                        if (data.weights && typeof data.weights === 'object') {
                            const labels = {
                                ordinary_request: 'درخواست معمولی',
                                text_analysis_or_recommendation: 'تحلیل متن یا پیشنهاد',
                                batch_request: 'درخواست دسته‌ای',
                                image_or_face_verification: 'تصویر یا تأیید چهره',
                                model_training: 'آموزش مدل'
                            };
                            const weightTitle = document.createElement('h3');
                            weightTitle.textContent = 'وزن مصرف عملیات';
                            output.appendChild(weightTitle);
                            const weightTable = document.createElement('table');
                            weightTable.className = 'widefat striped';
                            Object.keys(data.weights).forEach(function (key) {
                                const row = document.createElement('tr');
                                const name = document.createElement('td');
                                name.textContent = labels[key] || key;
                                const value = document.createElement('td');
                                value.textContent = String(data.weights[key]) + ' اعتبار';
                                row.appendChild(name);
                                row.appendChild(value);
                                weightTable.appendChild(row);
                            });
                            output.appendChild(weightTable);
                            const note = document.createElement('p');
                            note.textContent = 'وزن‌های مصرف فعلی موقت‌اند و تا تکمیل اندازه‌گیری هزینه نهایی تلقی نمی‌شوند.';
                            output.appendChild(note);
                        }
                    } catch (error) {
                        output.textContent = 'خطا در دریافت سهمیه: ' + error.message;
                    } finally {
                        button.disabled = false;
                        button.textContent = 'به‌روزرسانی مصرف';
                    }
                });
            })();
            </script>

            <hr>
            <h2>📋 سرویس‌ها و وابستگی‌ها</h2>
            <table class="wp-list-table widefat striped" style="max-width:780px">
                <thead><tr><th>سرویس</th><th>پورت</th><th>مدل</th><th>وابستگی</th></tr></thead>
                <tbody>
                    <tr><td>ML Service (Matching)</td><td>:8007</td><td>Cosine Similarity</td><td>embedded_ai:8100, Redis</td></tr>
                    <tr><td>Embedded AI</td><td>:8104</td><td>MiniLM-L12 multilingual</td><td>Redis</td></tr>
                    <tr><td>Personality</td><td>:8101</td><td>HuggingFace (محلی)</td><td>volume: /models</td></tr>
                    <tr><td>AI Assistant</td><td>:8022</td><td>Rule + NLP</td><td>Redis</td></tr>
                    <tr><td>AI Support</td><td>:8016</td><td>BERT فارسی</td><td>volume: /app/models</td></tr>
                </tbody>
            </table>

            <div class="notice notice-info inline" style="margin-top:16px;max-width:780px">
                <p>⚠️ <strong>نکته:</strong> سرویس <code>personality</code> اولین بار کند است — مدل lazy-load می‌شود.
                سرویس‌های <code>personality</code> و <code>ai_support</code> به volume با مدل‌های دانلود شده نیاز دارند.</p>
            </div>
        </div>

        <script>
        document.getElementById('mp-test-btn').addEventListener('click', function() {
            const btn = this, res = document.getElementById('mp-test-result');
            btn.disabled = true; res.style.display = 'block'; res.textContent = '⏳ بررسی (ممکن است ۱۰ ثانیه طول بکشد)...';
            fetch(ajaxurl, {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'action=matching_pack_test&nonce=<?php echo wp_create_nonce('mp_nonce'); ?>'
            }).then(r => r.json()).then(d => {
                res.textContent = JSON.stringify(d, null, 2);
            }).catch(e => res.textContent = '❌ ' + e.message)
            .finally(() => btn.disabled = false);
        });
        </script>
        <?php
    }

    public function ajax_test(): void {
        check_ajax_referer('mp_nonce', 'nonce');
        if (!current_user_can('manage_options')) {
            wp_send_json_error(['message' => 'Unauthorized'], 403);
        }
        wp_send_json(ApiClient::get_instance()->health_check());
    }
    public function ajax_usage(): void {
        check_ajax_referer('mp_nonce', 'nonce');
        if (!current_user_can('manage_options')) {
            wp_send_json_error(['message' => 'Unauthorized'], 403);
        }
        $usage = ApiClient::get_instance()->get_usage();
        if (isset($usage['error'])) {
            wp_send_json_error(['message' => $usage['error']], 502);
        }
        wp_send_json_success($usage);
    }

}
