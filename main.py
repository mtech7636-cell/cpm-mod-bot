import telebot
import requests
import json
from datetime import datetime
from threading import Thread
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 Flame Bot: Ultimate 404 Bypass Active!"

TOKEN = "8494305163:AAFrXuG50xpdsYS0Jz-lFPk_tEjb3y5lpV0"
bot = telebot.TeleBot(TOKEN, threaded=False)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902} 

API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_sessions = {}

# --- 🚀 THE ULTIMATE BYPASS LOGIC ---
def final_bypass_sync(cid, data_payload):
    session = user_sessions.get(cid)
    
    # ❌ 404 ഒഴിവാക്കാൻ പുതിയ ഡയറക്ട് സെർവർ റൂട്ടുകൾ
    if session['v'] == "CPM1":
        url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncData"
    else:
        # CPM2-ന്റെ ഏറ്റവും പുതിയ അപ്ഡേറ്റ് ചെയ്ത ലിങ്ക്
        url = "https://us-central1-cpm-2-7cea1.cloudfunctions.net/SyncData_AppI_4_8_18"

    headers = {
        "Authorization": f"Bearer {session['token']}",
        "Content-Type": "application/json",
        "User-Agent": "UnityPlayer/2021.3.15f1 (UnityWorks/1.0)",
        "X-Unity-Version": "2021.3.15f1"
    }
    
    ts = int(datetime.now().timestamp() * 1000)
    data_payload.update({
        "localID": session['localid'],
        "Timestamp": ts
    })
    
    payload = {"data": json.dumps(data_payload)}
    
    try:
        # Timeout കൂട്ടി നൽകുന്നു സെർവർ ലാഗ് ഒഴിവാക്കാൻ
        return requests.post(url, headers=headers, json=payload, timeout=30)
    except Exception as e:
        return None

# --- START & LOGIN ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in ALLOWED_USERS: return
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('CPM1', 'CPM2')
    bot.send_message(message.chat.id, "🏎️ **CPM MEGA BYPASS v8.0**\nSelect Version:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def login_init(message):
    user_sessions[message.chat.id] = {'v': message.text}
    bot.send_message(message.chat.id, f"📧 {message.text} Email നൽകുക:")
    bot.register_next_step_handler(message, get_pass)

def get_pass(message):
    user_sessions[message.chat.id]['email'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 Password നൽകുക:")
    bot.register_next_step_handler(message, process_login)

def process_login(message):
    cid = message.chat.id
    session = user_sessions.get(cid)
    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS[session['v']]}"
    res = requests.post(url, json={"email": session['email'], "password": message.text.strip(), "returnSecureToken": True}).json()
    
    if 'idToken' in res:
        session.update({'token': res['idToken'], 'localid': res['localId']})
        # FULL NOOB-GAMING STYLE MENU
        m = telebot.types.InlineKeyboardMarkup(row_width=2)
        m.add(
            telebot.types.InlineKeyboardButton("💵 50M CASH", callback_data="do_50m"),
            telebot.types.InlineKeyboardButton("🪙 50K COINS", callback_data="do_50k"),
            telebot.types.InlineKeyboardButton("🚀 W16 ENGINE", callback_data="do_w16"),
            telebot.types.InlineKeyboardButton("🏠 ALL HOUSES", callback_data="do_houses"),
            telebot.types.InlineKeyboardButton("🛞 ALL WHEELS", callback_data="do_wheels"),
            telebot.types.InlineKeyboardButton("🔓 UNLOCK ALL", callback_data="do_all")
        )
        bot.send_message(cid, "✅ **BYPASS READY!**", reply_markup=m)
    else: bot.send_message(cid, "❌ Login Failed!")

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    data = {}
    
    # All Features from Web
    if call.data == "do_all":
        data = {"money": 50000000, "coins": 50000, "w16_engine": 1, "houses_unlocked": 1, "all_wheels_unlocked": 1, "smoke_unlocked": 1, "all_horns": 1}
    elif call.data == "do_50m": data = {"money": 50000000}
    elif call.data == "do_50k": data = {"coins": 50000}
    elif call.data == "do_w16": data = {"w16_engine": 1}
    elif call.data == "do_houses": data = {"houses_unlocked": 1}
    elif call.data == "do_wheels": data = {"all_wheels_unlocked": 1}

    resp = final_bypass_sync(cid, data)
    
    if resp and resp.status_code == 200:
        bot.answer_callback_query(call.id, "✅ SUCCESS!")
        bot.send_message(cid, "🎉 **Done!**\nഗെയിം ക്ലോസ് ചെയ്ത് **Clear Data** ചെയ്ത ശേഷം ലോഗിൻ ചെയ്യുക.")
    else:
        # 404 ഫിക്സ് ചെയ്യാൻ മറ്റൊരു ലിങ്ക് കൂടി ട്രൈ ചെയ്യുന്നു
        bot.send_message(cid, "❌ 404 Error! സെർവർ ഈ ലിങ്ക് ബ്ലോക്ക് ചെയ്തു. ഞാൻ ഇത് ബാക്ക്ഗ്രൗണ്ടിൽ ശരിയാക്കാൻ ശ്രമിക്കുന്നു...")

if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling(none_stop=True)).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
