from flask import Flask, render_template_string, request, jsonify, session
import discord
import asyncio
import threading
import random
import json
import os

app = Flask(__name__)
app.secret_key = "syropanel_gizli_anahtar_guvenlik"

VERI_DOSYASI = "ayarlar.json"
SIFRE = "456200"

default_botlar = {
    f"bot_{i}": {
        "ad": f"Bot {i}",
        "token": "BURAYA_TOKEN_YAZ",
        "kanal_id": 123456789012345678,
        "metinler": "Selamlar!\nNasılsınız?\nİyi günler dilerim!",
        "etiket": "@",
        "sure": 10.0,
        "sirali": False,
        "index": 0,
        "aktif": False
    } for i in range(1, 9)
}

def ayarlari_yukle():
    if os.path.exists(VERI_DOSYASI):
        try:
            with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
                kayitli_veri = json.load(f)
                for b_id, b_data in default_botlar.items():
                    if b_id in kayitli_veri:
                        b_data.update(kayitli_veri[b_id])
                        b_data["client"] = None
                        b_data["thread"] = None
                return default_botlar
        except Exception as e:
            print(f"Ayarlar okunurken hata oluştu: {e}")
    
    for b_id in default_botlar:
        default_botlar[b_id]["client"] = None
        default_botlar[b_id]["thread"] = None
    return default_botlar

botlar = ayarlari_yukle()

def ayarlari_kaydet():
    temiz_veri = {}
    for b_id, b_data in botlar.items():
        temiz_veri[b_id] = {
            "ad": b_data["ad"],
            "token": b_data["token"],
            "kanal_id": b_data["kanal_id"],
            "metinler": b_data["metinler"],
            "etiket": b_data["etiket"],
            "sure": b_data["sure"],
            "sirali": b_data["sirali"],
            "index": b_data["index"],
            "aktif": b_data["aktif"]
        }
    try:
        with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(temiz_veri, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ayarlar kaydedilirken hata oluştu: {e}")

def bot_olustur(bot_id):
    client = discord.Client()
    bot_veri = botlar[bot_id]

    async def arkaplan_mesaj_dongusu():
        await client.wait_until_ready()
        while not client.is_closed():
            if bot_veri["aktif"]:
                kanal = client.get_channel(bot_veri["kanal_id"])
                if kanal:
                    try:
                        ham_metinler = bot_veri["metinler"].splitlines()
                        temiz_metinler = [m.strip() for m in ham_metinler if m.strip()]
                        
                        if temiz_metinler:
                            if bot_veri["sirali"]:
                                if bot_veri["index"] >= len(temiz_metinler):
                                    bot_veri["index"] = 0
                                
                                secilen_metin = temiz_metinler[bot_veri["index"]]
                                bot_veri["index"] += 1
                            else:
                                secilen_metin = random.choice(temiz_metinler)

                            etiket = bot_veri["etiket"].strip()
                            if etiket:
                                gonderilecek_mesaj = f"{secilen_metin} {etiket}"
                            else:
                                gonderilecek_mesaj = secilen_metin
                            
                            await kanal.send(gonderilecek_mesaj)
                            print(f"[{bot_veri['ad']}] Gönderildi: {gonderilecek_mesaj}")
                    except Exception as e:
                        print(f"[{bot_veri['ad']}] Hata oluştu: {e}")
            await asyncio.sleep(float(bot_veri["sure"]))

    @client.event
    async def on_ready():
        print(f"[{bot_veri['ad']}] Giriş yaptı: {client.user}")
        client.loop.create_task(arkaplan_mesaj_dongusu())

    return client

def bot_run_thread(bot_id):
    client = bot_olustur(bot_id)
    botlar[bot_id]["client"] = client
    try:
        client.run(botlar[bot_id]["token"])
    except Exception as e:
        print(f"[{botlar[bot_id]['ad']}] Başlatma hatası: {e}")

for b_id, bot in botlar.items():
    if bot["aktif"] and bot["token"] != "BURAYA_TOKEN_YAZ":
        t = threading.Thread(target=bot_run_thread, args=(b_id,))
        t.daemon = True
        t.start()
        bot["thread"] = t

login_tasarimi = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Syropanel - Giriş</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #13111c; color: #e0dced; margin: 0; height: 100vh; display: flex; justify-content: center; align-items: center; }
        .login-box { background: #1e1a29; padding: 30px; border-radius: 14px; width: 320px; box-shadow: 0 8px 25px rgba(88, 43, 133, 0.4); border: 1px solid #362d4e; text-align: center; }
        h1 { color: #a270ff; margin-bottom: 20px; font-size: 22px; }
        input[type="password"] { width: 100%; padding: 10px; margin: 15px 0; background: #13111c; border: 1px solid #3f335c; color: #fff; border-radius: 6px; box-sizing: border-box; outline: none; text-align: center; font-size: 15px; }
        input:focus { border-color: #8c41ff; }
        button { width: 100%; padding: 10px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; background: #7c3aed; color: white; transition: 0.2s; }
        button:hover { background: #6d28d9; }
        .error { color: #ef4444; font-size: 12px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>💜 SYROPANEL</h1>
        <form method="POST" action="/giris">
            <input type="password" name="sifre" placeholder="Panelin Şifresini Girin" required autofocus>
            <button type="submit">Giriş Yap</button>
            {% if hata %}
                <div class="error">Şifre hatalı!</div>
            {% endif %}
        </form>
    </div>
</body>
</html>
"""

html_tasarimi = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Gelişmiş Bot Kontrol Paneli</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #13111c; color: #e0dced; margin: 0; padding: 40px 20px; display: flex; flex-direction: column; align-items: center; }
        h1 { color: #a270ff; margin-bottom: 30px; letter-spacing: 1px; text-align: center; }
        .bot-container { display: flex; flex-wrap: wrap; gap: 25px; justify-content: center; max-width: 1300px; width: 100%; }
        .panel { background: #1e1a29; padding: 22px; border-radius: 14px; width: 370px; box-shadow: 0 8px 25px rgba(88, 43, 133, 0.3); border: 1px solid #362d4e; box-sizing: border-box; }
        .panel h3 { color: #c4a1ff; margin-top: 0; margin-bottom: 12px; border-bottom: 1px solid #3f335c; padding-bottom: 8px; display: flex; justify-content: space-between; align-items: center; font-size: 16px; }
        label { display: block; margin-top: 10px; font-size: 12px; color: #bcaedb; font-weight: 500; }
        input[type="text"], input[type="number"], textarea { width: 100%; padding: 8px; margin-top: 4px; background: #13111c; border: 1px solid #3f335c; color: #fff; border-radius: 6px; box-sizing: border-box; outline: none; font-size: 13px; }
        input:focus, textarea:focus { border-color: #8c41ff; }
        textarea { resize: vertical; height: 75px; }
        .checkbox-container { display: flex; align-items: center; gap: 8px; margin-top: 12px; font-size: 12px; color: #c4a1ff; cursor: pointer; }
        .checkbox-container input { width: 16px; height: 16px; cursor: pointer; accent-color: #7c3aed; }
        .buttons { display: flex; justify-content: space-between; margin-top: 15px; gap: 8px; }
        button { flex: 1; padding: 9px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 12px; }
        .btn-start { background: #7c3aed; color: white; }
        .btn-stop { background: #dc2626; color: white; }
        .status { text-align: center; margin-top: 12px; font-weight: bold; font-size: 13px; }
        .badge { font-size: 10px; padding: 2px 6px; border-radius: 10px; background: #2d2442; color: #a855f7; }
        .hint { font-size: 10px; color: #9ca3af; margin-top: 2px; }
    </style>
</head>
<body>
    <h1>💜 SYROPANEL</h1>
    
    <div class="bot-container">
        {% for b_id, bot in botlar.items() %}
        <div class="panel">
            <h3><span>🤖 {{ bot.ad }}</span> <span class="badge">{{ b_id }}</span></h3>
            
            <label>Token:</label>
            <input type="text" id="token_{{ b_id }}" value="{{ bot.token }}">

            <label>Kanal ID:</label>
            <input type="number" id="kanal_{{ b_id }}" value="{{ bot.kanal_id }}">

            <label>Metin Havuzu (Her satıra bir cümle yazın):</label>
            <textarea id="metinler_{{ b_id }}">{{ bot.metinler }}</textarea>
            <div class="hint">Alt alta istediğin kadar satır ekleyebilirsin.</div>

            <label class="checkbox-container">
                <input type="checkbox" id="sirali_{{ b_id }}" {% if bot.sirali %}checked{% endif %}>
                <span>Sıralı Gönderim (Yukarıdan Aşağıya / Repeat)</span>
            </label>

            <label>Sonuna Eklenecek Etiket:</label>
            <input type="text" id="etiket_{{ b_id }}" value="{{ bot.etiket }}">
            <div class="hint">Örn: @emre veya boş bırakabilirsiniz.</div>
            
            <label>Süre (Saniye, örn: 0.5 veya 1.25):</label>
            <input type="number" step="any" id="sure_{{ b_id }}" value="{{ bot.sure }}">
            
            <div class="buttons">
                <button class="btn-start" onclick="botGuncelle('{{ b_id }}', true)">Başlat / Kaydet</button>
                <button class="btn-stop" onclick="botGuncelle('{{ b_id }}', false)">Durdur</button>
            </div>
            
            <div class="status">
                Durum: 
                {% if bot.aktif %}
                    <span style="color: #a855f7;">Çalışıyor 🚀</span>
                {% else %}
                    <span style="color: #ef4444;">Durduruldu 🛑</span>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>

    <script>
        function botGuncelle(botId, aktifMi) {
            const token = document.getElementById('token_' + botId).value;
            const kanal = document.getElementById('kanal_' + botId).value;
            const metinler = document.getElementById('metinler_' + botId).value;
            const sirali = document.getElementById('sirali_' + botId).checked;
            const etiket = document.getElementById('etiket_' + botId).value;
            const sure = document.getElementById('sure_' + botId).value;

            fetch('/guncelle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    bot_id: botId, 
                    aktif: aktifMi, 
                    token: token, 
                    kanal_id: kanal, 
                    metinler: metinler, 
                    sirali: sirali,
                    etiket: etiket,
                    sure: sure 
                })
            })
            .then(response => response.json())
            .then(data => {
                location.reload();
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    if not session.get('giris_yapildi'):
        return render_template_string(login_tasarimi, hata=False)
    return render_template_string(html_tasarimi, botlar=botlar)

@app.route('/giris', methods=['POST'])
def giris():
    kullanici_sifresi = request.form.get('sifre')
    if kullanici_sifresi == SIFRE:
        session['giris_yapildi'] = True
        return index()
    else:
        return render_template_string(login_tasarimi, hata=True)

@app.route('/guncelle', methods=['POST'])
def guncelle():
    if not session.get('giris_yapildi'):
        return jsonify({"durum": "yetkisiz"}), 401

    data = request.json
    b_id = data.get('bot_id')
    
    if b_id in botlar:
        bot = botlar[b_id]
        bot['token'] = data.get('token', bot['token'])
        bot['kanal_id'] = int(data.get('kanal_id', bot['kanal_id']))
        bot['metinler'] = data.get('metinler', bot['metinler'])
        bot['sirali'] = data.get('sirali', bot['sirali'])
        bot['etiket'] = data.get('etiket', bot['etiket'])
        bot['sure'] = float(data.get('sure', bot['sure']))
        bot['aktif'] = data.get('aktif', bot['aktif'])
        
        ayarlari_kaydet()
        
        if bot['aktif'] and bot['client'] is None and bot['token'] != "BURAYA_TOKEN_YAZ":
            t = threading.Thread(target=bot_run_thread, args=(b_id,))
            t.daemon = True
            t.start()
            bot['thread'] = t

    return jsonify({"durum": "başarılı"})

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
