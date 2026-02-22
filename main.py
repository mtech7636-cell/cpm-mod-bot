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
    return "🔥 CPM Master Bot is Online!"

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

# --- ACCURATE ENDPOINTS TO FIX 404 ---
def get_endpoint(version):
    if version == "CPM1":
        return "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncData"
    else:
        # CPM2-ന് ഈ ലിങ്ക് ആണ് കൃത്യം
        return "https://us-central1-cpm-2-7cea1.cloudfunctions.net/SyncData_AppI"

def sync_data(cid, data_payload):
    session = user_sessions.get(cid)
    url = get_endpoint(session['v'])
    
    headers = {
        "Authorization": f"Bearer {session['token']}",
        "Content-Type": "application/json",
        "User-Agent": "BestHTTP/2 v2.4.0"
    }
    
    ts = int(datetime.now().timestamp() * 1000)
    data_payload.update({
        "localID": session['localid'],
        "Timestamp": ts
    })
    
    payload = {"data": json.dumps(data_payload)}
    return requests.post(url, headers=headers, json=payload)

# --- BOT COMMANDS & LOGIN ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in ALLOWED_USERS:
        bot.send_message(uid, f"❌ No Access! ID: `{uid}`")
        return
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('CPM1', 'CPM2')
    bot.send_message(message.chat.id, "🏎️ **CPM MEGA v6.0**\nSelect Version:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def login_init(message):
    user_sessions[message.chat.id] = {'v': message.text}
    bot.send_message(message.chat.id, f"📧 Enter {message.text} Email:")
    bot.register_next_step_handler(message, get_pass)

def get_pass(message):
    user_sessions[message.chat.id]['email'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 Enter Password:")
    bot.register_next_step_handler(message, process_login)

def process_login(message):
    cid = message.chat.id
    session = user_sessions.get(cid)
    api_key = API_KEYS[session['v']]
    
    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={api_key}"
    res = requests.post(url, json={"email": session['email'], "password": message.text.strip(), "returnSecureToken": True}).json()
    
    if 'idToken' in res:
        session.update({'token': res['idToken'], 'localid': res['localId']})
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            telebot.types.InlineKeyboardButton("🔓 UNLOCK ALL (NO 404)", callback_data="all"),
            telebot.types.InlineKeyboardButton("💰 50M CASH", callback_data="money"),
            telebot.types.InlineKeyboardButton("🚀 W16 & EXTREME", callback_data="w16")
        )
        bot.send_message(cid, f"✅ **Logged in to {session['v']}!**", reply_markup=markup)
    else:
        bot.send_message(cid, "❌ Login Failed! Email/Password തെറ്റാണ്.")

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    session = user_sessions.get(cid)
    if not session: return

    data = {}
    if call.data == "all":
        data = {"money": 50000000, "coins": 50000, "w16_engine": 1, "houses_unlocked": 1, "all_wheels_unlocked": 1, "all_horns": 1, "smoke_unlocked": 1}
    elif call.data == "money":
        data = {"money": 50000000}
    elif call.data == "w16":
        data = {"w16_engine": 1, "engine_damage": 0}

    resp = sync_data(cid, data)
    
    if resp.status_code == 200:
        bot.answer_callback_query(call.id, "✅ SUCCESS!")
        bot.send_message(cid, f"🎉 **{session['v']} Updated!**\n\nഗെയിം ക്ലോസ് ചെയ്ത് **Clear Data** ചെയ്ത ശേഷം ലോഗിൻ ചെയ്യുക.")
    else:
        bot.send_message(cid, f"❌ Failed! Error: {resp.status_code}\nസെർവർ ലിങ്ക് പ്രശ്നമാണ്.")

if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling(none_stop=True)).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
