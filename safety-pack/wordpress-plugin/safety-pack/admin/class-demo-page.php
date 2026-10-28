<?php
namespace SafetyPack;

class DemoPage {
    private static ?DemoPage $instance = null;

    public static function get_instance(): DemoPage {
        if (self::$instance === null) self::$instance = new self();
        return self::$instance;
    }

    private function __construct() {
        add_action('admin_menu', [$this, 'add_menu']);
        add_action('wp_ajax_safety_pack_demo_text',   [$this, 'ajax_demo_text']);
        add_action('wp_ajax_safety_pack_demo_verify', [$this, 'ajax_demo_verify']);
        add_action('wp_ajax_safety_pack_demo_image',  [$this, 'ajax_demo_image']);
    }

    public function add_menu(): void {
        add_submenu_page('safety-pack-settings', 'دمو زنده', '🔬 دمو زنده',
            'manage_options', 'safety-pack-demo', [$this, 'render']);
    }

    public function render(): void {
        if (!License::is_active()) {
            echo '<div class="wrap"><div class="notice notice-error"><p>ابتدا License key را وارد کنید.</p></div></div>';
            return;
        }
        $nonce_text   = wp_create_nonce('sp_demo_text');
        $nonce_verify = wp_create_nonce('sp_demo_verify');
        $nonce_image  = wp_create_nonce('sp_demo_image');
        ?>
        <div class="wrap" dir="rtl">
            <h1>🔬 دمو زنده — Safety Pack AI</h1>

            <nav class="nav-tab-wrapper" style="margin-bottom:20px">
                <a class="nav-tab nav-tab-active" data-tab="moderation">💬 مدیریت متن</a>
                <a class="nav-tab" data-tab="verification">🪪 تأیید چهره</a>
                <a class="nav-tab" data-tab="image">🖼️ بررسی تصویر</a>
            </nav>

            <!-- Tab: Moderation -->
            <div id="tab-moderation" class="sp-tab">
                <div class="card" style="max-width:720px;padding:20px">
                    <h2>💬 مدیریت محتوای متنی</h2>
                    <p>متنی وارد کنید تا سیستم بررسی کنه مناسبه یا نه. سرویس دو لایه داره: rule-based سریع + semantic AI.</p>

                    <label><strong>متن:</strong></label>
                    <textarea id="mod-text" rows="4" style="width:100%;direction:rtl;margin:8px 0"
                        placeholder="پیام، بیو، یا کامنت کاربر را اینجا بنویسید...">لطفاً آیدی تلگرامت رو بده تا خارج از اپ حرف بزنیم</textarea>

                    <label><strong>نوع محتوا:</strong></label>
                    <select id="mod-context" style="margin:0 8px">
                        <option value="message">پیام (message)</option>
                        <option value="bio">بیوگرافی (bio)</option>
                        <option value="comment">کامنت (comment)</option>
                    </select>
                    <br><br>
                    <button class="button button-primary" id="mod-single-btn">🔍 بررسی متن</button>
                    <div class="sp-result" id="result-mod"></div>

                    <hr>
                    <h3>بررسی دسته‌ای</h3>
                    <textarea id="mod-batch" rows="5" style="width:100%;direction:rtl;font-size:13px"
                        placeholder="هر خط یه متن جداگانه...">سلام چطوری؟
شماره‌ات رو بده
خرید و فروش محصولات با قیمت مناسب
من دوستت دارم
t.me/channel_xyz</textarea>
                    <br><br>
                    <button class="button button-secondary" id="mod-batch-btn">📋 بررسی دسته‌ای</button>
                    <div class="sp-result" id="result-mod-batch"></div>
                </div>
            </div>

            <!-- Tab: Verification -->
            <div id="tab-verification" class="sp-tab" style="display:none">
                <div class="card" style="max-width:720px;padding:20px">
                    <h2>🪪 تأیید هویت با چهره</h2>
                    <p>دو تصویر آپلود کنید — سلفی کاربر و عکس پروفایل. سیستم با DeepFace/Facenet مطابقت رو بررسی می‌کنه.</p>
                    <p style="color:#856404;background:#fff3cd;padding:8px;border-radius:4px">
                        ⚠️ تصاویر فقط برای پردازش ارسال می‌شن و ذخیره نمی‌شن.
                    </p>

                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:16px 0">
                        <div>
                            <label><strong>سلفی کاربر:</strong></label><br>
                            <input type="file" id="verify-selfie" accept="image/*" style="margin-top:8px">
                            <div id="preview-selfie" style="margin-top:8px"></div>
                        </div>
                        <div>
                            <label><strong>عکس پروفایل:</strong></label><br>
                            <input type="file" id="verify-profile" accept="image/*" style="margin-top:8px">
                            <div id="preview-profile" style="margin-top:8px"></div>
                        </div>
                    </div>

                    <button class="button button-primary" id="verify-btn">🔍 بررسی مطابقت چهره</button>
                    <div class="sp-result" id="result-verify"></div>
                </div>
            </div>

            <!-- Tab: Image -->
            <div id="tab-image" class="sp-tab" style="display:none">
                <div class="card" style="max-width:720px;padding:20px">
                    <h2>🖼️ بررسی و تحلیل تصویر</h2>
                    <p>تصویر آپلود کنید تا:</p>
                    <ul>
                        <li>EXIF metadata پاک بشه (حریم خصوصی)</li>
                        <li>محتوای NSFW تشخیص داده بشه</li>
                        <li>کیفیت و وجود چهره بررسی بشه</li>
                    </ul>

                    <input type="file" id="img-file" accept="image/*" style="margin:12px 0">
                    <div id="preview-img" style="margin-bottom:12px"></div>

                    <div style="display:flex;gap:12px">
                        <button class="button button-primary"   id="img-upload-btn">🛡️ آپلود + بررسی NSFW</button>
                        <button class="button button-secondary" id="img-analyze-btn">🔎 تحلیل کامل</button>
                    </div>
                    <div class="sp-result" id="result-img"></div>
                </div>
            </div>
        </div>

        <style>
        .sp-result {
            margin-top:16px; padding:14px;
            background:#1e1e2e; color:#cdd6f4;
            border-radius:6px; font-family:monospace;
            font-size:13px; direction:ltr;
            display:none; white-space:pre-wrap;
        }
        .sp-result.loading { opacity:.6 }
        .sp-preview img { max-height:160px; border-radius:6px; border:1px solid #ddd; }
        </style>

        <script>
        // Tab switch
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', function(e) {
                e.preventDefault();
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('nav-tab-active'));
                document.querySelectorAll('.sp-tab').forEach(t => t.style.display = 'none');
                this.classList.add('nav-tab-active');
                document.getElementById('tab-' + this.dataset.tab).style.display = 'block';
            });
        });

        // Image preview helper
        function setupPreview(inputId, previewId) {
            document.getElementById(inputId).addEventListener('change', function() {
                const file = this.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = e => {
                    document.getElementById(previewId).innerHTML =
                        '<img src="' + e.target.result + '" style="max-height:120px;border-radius:6px;border:1px solid #ddd">';
                };
                reader.readAsDataURL(file);
            });
        }
        setupPreview('verify-selfie', 'preview-selfie');
        setupPreview('verify-profile', 'preview-profile');
        setupPreview('img-file', 'preview-img');

        // Helper: show result
        function showResult(id, data) {
            const el = document.getElementById(id);
            el.style.display = 'block';
            el.classList.remove('loading');
            el.textContent = JSON.stringify(data, null, 2);
        }
        function setLoading(id) {
            const el = document.getElementById(id);
            el.style.display = 'block';
            el.classList.add('loading');
            el.textContent = '⏳ در حال پردازش...';
        }

        // ── Moderation: single ──────────────────────────────────────────
        document.getElementById('mod-single-btn').addEventListener('click', function() {
            setLoading('result-mod');
            const fd = new FormData();
            fd.append('action', 'safety_pack_demo_text');
            fd.append('nonce', '<?php echo $nonce_text; ?>');
            fd.append('text', document.getElementById('mod-text').value);
            fd.append('context', document.getElementById('mod-context').value);
            fd.append('batch', '0');
            fetch(ajaxurl, {method:'POST', body:fd})
                .then(r => r.json()).then(d => showResult('result-mod', d))
                .catch(e => showResult('result-mod', {error: e.message}));
        });

        // ── Moderation: batch ───────────────────────────────────────────
        document.getElementById('mod-batch-btn').addEventListener('click', function() {
            setLoading('result-mod-batch');
            const fd = new FormData();
            fd.append('action', 'safety_pack_demo_text');
            fd.append('nonce', '<?php echo $nonce_text; ?>');
            fd.append('texts', document.getElementById('mod-batch').value);
            fd.append('context', 'message');
            fd.append('batch', '1');
            fetch(ajaxurl, {method:'POST', body:fd})
                .then(r => r.json()).then(d => showResult('result-mod-batch', d))
                .catch(e => showResult('result-mod-batch', {error: e.message}));
        });

        // ── Verification ────────────────────────────────────────────────
        document.getElementById('verify-btn').addEventListener('click', function() {
            const selfie  = document.getElementById('verify-selfie').files[0];
            const profile = document.getElementById('verify-profile').files[0];
            if (!selfie || !profile) {
                alert('هر دو تصویر را انتخاب کنید'); return;
            }
            setLoading('result-verify');
            const fd = new FormData();
            fd.append('action', 'safety_pack_demo_verify');
            fd.append('nonce', '<?php echo $nonce_verify; ?>');
            fd.append('selfie', selfie);
            fd.append('profile', profile);
            fetch(ajaxurl, {method:'POST', body:fd})
                .then(r => r.json()).then(d => showResult('result-verify', d))
                .catch(e => showResult('result-verify', {error: e.message}));
        });

        // ── Image: upload ───────────────────────────────────────────────
        document.getElementById('img-upload-btn').addEventListener('click', function() {
            const file = document.getElementById('img-file').files[0];
            if (!file) { alert('تصویر انتخاب کنید'); return; }
            setLoading('result-img');
            const fd = new FormData();
            fd.append('action', 'safety_pack_demo_image');
            fd.append('nonce', '<?php echo $nonce_image; ?>');
            fd.append('file', file);
            fd.append('mode', 'upload');
            fetch(ajaxurl, {method:'POST', body:fd})
                .then(r => r.json()).then(d => showResult('result-img', d))
                .catch(e => showResult('result-img', {error: e.message}));
        });

        // ── Image: analyze ──────────────────────────────────────────────
        document.getElementById('img-analyze-btn').addEventListener('click', function() {
            const file = document.getElementById('img-file').files[0];
            if (!file) { alert('تصویر انتخاب کنید'); return; }
            setLoading('result-img');
            const fd = new FormData();
            fd.append('action', 'safety_pack_demo_image');
            fd.append('nonce', '<?php echo $nonce_image; ?>');
            fd.append('file', file);
            fd.append('mode', 'analyze');
            fetch(ajaxurl, {method:'POST', body:fd})
                .then(r => r.json()).then(d => showResult('result-img', d))
                .catch(e => showResult('result-img', {error: e.message}));
        });
        </script>
        <?php
    }

    // ── AJAX Handlers ─────────────────────────────────────────────────────

    public function ajax_demo_text(): void {
        check_ajax_referer('sp_demo_text', 'nonce');
        if (!current_user_can('manage_options')) wp_die('Unauthorized');
        $client  = ApiClient::get_instance();
        $is_batch = (int) ($_POST['batch'] ?? 0);

        if ($is_batch) {
            $texts = array_filter(array_map('trim', explode("\n", $_POST['texts'] ?? '')));
            wp_send_json($client->moderate_batch(array_values($texts), $_POST['context'] ?? 'message'));
        } else {
            wp_send_json($client->moderate_text(
                sanitize_textarea_field($_POST['text'] ?? ''),
                sanitize_text_field($_POST['context'] ?? 'message'),
            ));
        }
    }

    public function ajax_demo_verify(): void {
        check_ajax_referer('sp_demo_verify', 'nonce');
        if (!current_user_can('manage_options')) wp_die('Unauthorized');

        $selfie  = $_FILES['selfie']  ?? null;
        $profile = $_FILES['profile'] ?? null;
        if (!$selfie || !$profile || $selfie['error'] || $profile['error']) {
            wp_send_json(['error' => 'فایل‌ها نامعتبرند']);
        }

        $client = ApiClient::get_instance();
        wp_send_json($client->verify_face($selfie['tmp_name'], $profile['tmp_name']));
    }

    public function ajax_demo_image(): void {
        check_ajax_referer('sp_demo_image', 'nonce');
        if (!current_user_can('manage_options')) wp_die('Unauthorized');

        $file = $_FILES['file'] ?? null;
        if (!$file || $file['error']) {
            wp_send_json(['error' => 'فایل نامعتبر است']);
        }

        $client = ApiClient::get_instance();
        $mode   = sanitize_text_field($_POST['mode'] ?? 'upload');
        $result = $mode === 'analyze'
            ? $client->analyze_image($file['tmp_name'])
            : $client->upload_image($file['tmp_name']);

        wp_send_json($result);
    }
}
