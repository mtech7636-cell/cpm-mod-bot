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
    return "🔥 Flame Bot: 404 Fix Active"

TOKEN = "8494305163:AAFrXuG50xpdsYS0Jz-lFPk_tEjb3y5lpV0"
bot = telebot.TeleBot(TOKEN, threaded=False)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902} 

# --- UPDATED API KEYS ---
API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_sessions = {}

# --- NEW WORKING SYNC LOGIC ---
def sync_data(cid, data_payload):
    session = user_sessions.get(cid)
    headers = {
        "Authorization": f"Bearer {session['token']}",
        "Content-Type": "application/json",
        "User-Agent": "BestHTTP/2 v2.4.0",
        "X-Unity-Version": "2019.4.31f1"
    }
    
    ts = int(datetime.now().timestamp() * 1000)
    data_payload.update({
        "localID": session['localid'],
        "Timestamp": ts
    })
    
    # ❌ 404 ഒഴിവാക്കാനുള്ള പുതിയ ലിങ്കുകൾ
    if session['v'] == "CPM1":
        # CPM1 Latest Endpoint
        url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncData"
    else:
        # CPM2 Latest Endpoint (ഇതാണ് പലപ്പോഴും 404 വരുന്നത്)
        url = "https://us-central1-cpm-2-7cea1.cloudfunctions.net/SyncData_AppI"

    payload = {"data": json.dumps(data_payload)}
    return requests.post(url, headers=headers, json=payload)

# --- START & LOGIN ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in ALLOWED_USERS:
        bot.send_message(uid, f"❌ No Access! ID: `{uid}`")
        return
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('CPM1', 'CPM2')
    bot.send_message(message.chat.id, "🏎️ **FLAME MEGA v5.0**\nSelect Game Version:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def login_init(message):
    user_sessions[message.chat.id] = {'v': message.text}
    bot.send_message(message.chat.id, "📧 Enter Email:")
    bot.register_next_step_handler(message, get_pass)

def get_pass(message):
    user_sessions[message.chat.id]['email'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 Enter Password:")
    bot.register_next_step_handler(message, process_login)

def process_login(message):
    cid = message.chat.id
    session = user_sessions.get(cid)
    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS[session['v']]}"
    res = requests.post(url, json={"email": session['email'], "password": message.text.strip(), "returnSecureToken": True}).json()
    
    if 'idToken' in res:
        session.update({'token': res['idToken'], 'localid': res['localId']})
        m = telebot.types.InlineKeyboardMarkup(row_width=1)
        m.add(
            telebot.types.InlineKeyboardButton("🔓 UNLOCK ALL (REAL SYNC)", callback_data="do_all"),
            telebot.types.InlineKeyboardButton("💰 50M CASH", callback_data="do_money"),
            telebot.types.InlineKeyboardButton("🚀 W16 + ENGINE FIX", callback_data="do_w16")
        )
        bot.send_message(cid, "✅ **Logged In!**\nഎല്ലാം അൺലോക്ക് ചെയ്യാൻ താഴെ അമർത്തുക:", reply_markup=m)
    else: bot.send_message(cid, "❌ Login Failed!")

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    data = {}
    
    if call.data == "do_all":
        data = {"money": 50000000, "coins": 45000, "w16_engine": 1, "houses_unlocked": 1, "all_wheels_unlocked": 1, "smoke_unlocked": 1, "all_horns": 1, "engine_damage": 0}
    elif call.data == "do_money":
        data = {"money": 50000000}
    elif call.data == "do_w16":
        data = {"w16_engine": 1, "engine_damage": 0}

    resp = sync_data(cid, data)
    
    # 404 ഉണ്ടോ എന്ന് ചെക്ക് ചെയ്യുന്നു
    if resp.status_code == 200:
        bot.answer_callback_query(call.id, "✅ SUCCESS! SENT TO CLOUD.")
        bot.send_message(cid, "🎉 **Success!**\n\n1. ഗെയിം ക്ലോസ് ചെയ്യുക.\n2. **Clear Data** അടിക്കുക.\n3. ഗെയിമിൽ ലോഗിൻ ചെയ്ത് **Download Cloud Save** കൊടുക്കുക.")
    else:
        bot.send_message(cid, f"❌ Failed! Error: {resp.status_code}\nസെർവർ ലിങ്കിൽ പ്രശ്നമുണ്ട്.")

if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling(none_stop=True)).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
