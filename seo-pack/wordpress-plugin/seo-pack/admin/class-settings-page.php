<?php
namespace SeoPack;

class SettingsPage {

    private static ?SettingsPage $instance = null;

    public static function get_instance(): SettingsPage {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        add_action('admin_menu', [$this, 'add_menu']);
        add_action('admin_init', [$this, 'register_settings']);
        add_action('wp_ajax_seo_pack_test_connection', [$this, 'ajax_test_connection']);
        add_action('wp_ajax_seo_pack_usage', [$this, 'ajax_usage']);
        add_action('wp_ajax_seo_pack_generate_license', [$this, 'ajax_generate_license']);
    }

    public function add_menu(): void {
        add_menu_page(
            'SEO Pack AI',
            'SEO Pack AI',
            'manage_options',
            'seo-pack-settings',
            [$this, 'render_settings'],
            'dashicons-chart-line',
            80
        );
        add_submenu_page(
            'seo-pack-settings',
            'تنظیمات',
            'تنظیمات',
            'manage_options',
            'seo-pack-settings',
            [$this, 'render_settings']
        );
    }

    public function register_settings(): void {
        register_setting('seo_pack_options', 'seo_pack_license_key', [
            'sanitize_callback' => 'sanitize_text_field',
        ]);
        register_setting('seo_pack_options', 'seo_pack_api_url', [
            'sanitize_callback' => 'esc_url_raw',
            'default'           => 'https://api.yoursite.com/seo-pack',
        ]);
    }

    public function render_settings(): void {
        $license_key = get_option('seo_pack_license_key', '');
        $api_url     = get_option('seo_pack_api_url', 'https://api.yoursite.com/seo-pack');
        $is_active   = License::is_active();
        ?>
        <div class="wrap">
            <h1>⚙️ تنظیمات SEO Pack AI</h1>

            <?php if ($is_active): ?>
                <div class="notice notice-success inline"><p>✅ اتصال برقرار است — سرویس‌ها فعال هستند</p></div>
            <?php else: ?>
                <div class="notice notice-error inline"><p>❌ اتصال برقرار نیست — License key رو چک کنید</p></div>
            <?php endif; ?>

            <form method="post" action="options.php">
                <?php settings_fields('seo_pack_options'); ?>
                <table class="form-table">
                    <tr>
                        <th><label for="seo_pack_license_key">🔑 License Key</label></th>
                        <td>
                            <input
                                type="password"
                                id="seo_pack_license_key"
                                name="seo_pack_license_key"
                                value="<?php echo esc_attr($license_key); ?>"
                                class="regular-text"
                                placeholder="sk-xxxxxxxxxxxxxxxxxxxxxx"
                            />
                            <p class="description">License key که بعد از خرید دریافت کردید</p>
                        </td>
                    </tr>
                    <tr>
                        <th><label for="seo_pack_api_url">🌐 آدرس API</label></th>
                        <td>
                            <input
                                type="url"
                                id="seo_pack_api_url"
                                name="seo_pack_api_url"
                                value="<?php echo esc_attr($api_url); ?>"
                                class="regular-text"
                            />
                            <p class="description">آدرس Gateway سرویس‌های SEO</p>
                        </td>
                    </tr>
                </table>
                <?php submit_button('ذخیره تنظیمات'); ?>
            </form>

            <hr>
            <h2>🔌 تست اتصال</h2>
            <button id="seo-pack-test-btn" class="button button-secondary">تست اتصال به سرویس‌ها</button>
            <div id="seo-pack-test-result" style="margin-top:12px;padding:12px;background:#f8f8f8;border-radius:4px;display:none;font-family:monospace;font-size:13px;"></div>

            <hr>
            <h2>📊 مصرف و سهمیه</h2>
            <p>مصرف واقعی اعتبارهای Gateway و سقف دوره‌های ساعتی و ماهانه را مشاهده کنید.</p>
            <p class="description">این گزارش صورتحساب پولی، مالیات یا فاکتور نیست؛ فقط اعتبار مصرف‌شده در Gateway را نشان می‌دهد.</p>
            <button type="button" id="seo-pack-usage-btn" class="button button-secondary">به‌روزرسانی مصرف</button>
            <div id="seo-pack-usage-result" role="status" aria-live="polite"
                 style="margin-top:12px;max-width:760px;padding:12px;background:#f8f8f8;border-radius:6px">
                برای مشاهده آخرین مصرف و سهمیه، دکمه را انتخاب کنید.
            </div>
            <script>
            (function () {
                const button = document.getElementById('seo-pack-usage-btn');
                const output = document.getElementById('seo-pack-usage-result');
                if (!button || !output) return;
                const nonce = '<?php echo esc_js(wp_create_nonce('seo_pack_nonce')); ?>';
                const readNonNegative = function (value) {
                    if (value === null || value === undefined || value === '') return null;
                    const parsed = Number(value);
                    return Number.isFinite(parsed) && parsed >= 0 ? parsed : null;
                };
                button.addEventListener('click', async function () {
                    button.disabled = true;
                    button.textContent = 'در حال دریافت...';
                    output.textContent = 'در حال دریافت اطلاعات مصرف از Gateway...';
                    try {
                        const body = new URLSearchParams({action: 'seo_pack_usage', nonce: nonce});
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
                        [data.hourly, data.monthly].forEach(function (period) {
                            if (
                                readNonNegative(period.used) === null ||
                                readNonNegative(period.limit) === null ||
                                readNonNegative(period.remaining) === null
                            ) {
                                throw new Error('مقادیر مصرف و سقف کامل یا معتبر نیستند');
                            }
                        });
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
                            const used = readNonNegative(period.used);
                            const limit = readNonNegative(period.limit);
                            const remaining = readNonNegative(period.remaining);
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
            <h2>📊 وضعیت سرویس‌ها</h2>
            <table class="wp-list-table widefat striped" style="max-width:600px">
                <thead><tr><th>سرویس</th><th>پورت</th><th>عملکرد</th></tr></thead>
                <tbody>
                    <tr><td>AI SEO (پیش‌بینی ترافیک)</td><td>8021</td><td>predict/traffic · feedback/campaign</td></tr>
                    <tr><td>AEO Tracker (دیده‌شدن در AI)</td><td>8030</td><td>check-mentions · history</td></tr>
                    <tr><td>Backlink Quality</td><td>8032</td><td>trust-flow · topic-similarity</td></tr>
                    <tr><td>SEO Recommender</td><td>8033</td><td>recommend · train</td></tr>
                </tbody>
            </table>
        </div>

        <script>
        document.getElementById('seo-pack-test-btn').addEventListener('click', function() {
            const btn = this;
            const result = document.getElementById('seo-pack-test-result');
            btn.disabled = true;
            btn.textContent = 'در حال بررسی...';
            result.style.display = 'block';
            result.textContent = '⏳ در حال اتصال به سرویس‌ها...';

            fetch(ajaxurl, {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'action=seo_pack_test_connection&nonce=<?php echo wp_create_nonce('seo_pack_nonce'); ?>'
            })
            .then(r => r.json())
            .then(data => {
                const pre = document.createElement('pre');
                pre.textContent = JSON.stringify(data, null, 2);
                result.replaceChildren(pre);
            })
            .catch(e => { result.textContent = '❌ خطا: ' + e.message; })
            .finally(() => { btn.disabled = false; btn.textContent = 'تست اتصال به سرویس‌ها'; });
        });
        </script>
        <?php
    }

    public function ajax_test_connection(): void {
        check_ajax_referer('seo_pack_nonce', 'nonce');
        if (!current_user_can('manage_options')) wp_die('Unauthorized');
        $client = ApiClient::get_instance();
        wp_send_json($client->health_check());
    }
    public function ajax_usage(): void {
        check_ajax_referer('seo_pack_nonce', 'nonce');
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
