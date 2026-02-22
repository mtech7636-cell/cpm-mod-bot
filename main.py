import telebot
import requests
import json
from datetime import datetime
from threading import Thread
from flask import Flask
import os

# --- UPTIME SERVER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 Flame Mega Bot is Live & Stable!"

# --- BOT CONFIGURATION ---
TOKEN = "8494305163:AAFrXuG50xpdsYS0Jz-lFPk_tEjb3y5lpV0"
bot = telebot.TeleBot(TOKEN, threaded=False)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902} 

API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_sessions = {}

# --- MASTER SYNC LOGIC ---
def sync_data(cid, data_to_sync):
    session = user_sessions.get(cid)
    headers = {
        "Authorization": f"Bearer {session['token']}",
        "Content-Type": "application/json",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12;)" 
    }
    
    ts = int(datetime.now().timestamp() * 1000)
    data_to_sync.update({
        "localID": session['localid'],
        "Timestamp": ts
    })
    
    payload = {"data": json.dumps(data_to_sync)}
    
    if session['v'] == "CPM1":
        url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncData"
    else:
        url = "https://us-central1-cpm-2-7cea1.cloudfunctions.net/SyncData_AppI"

    return requests.post(url, headers=headers, json=payload)

# --- START & ADMIN ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in ALLOWED_USERS:
        bot.send_message(uid, f"⏳ Access ആവശ്യമുണ്ട്. ID: `{uid}`", parse_mode="Markdown")
        bot.send_message(ADMIN_ID, f"🔔 **New Request:** `{uid}`")
        return
    
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('CPM1', 'CPM2')
    bot.send_message(message.chat.id, "🔥 **FLAME MEGA TOOL**\nSelect Version:", reply_markup=markup)

@bot.message_handler(commands=['add'])
def add_user(message):
    if message.from_user.id == ADMIN_ID:
        try:
            new_id = int(message.text.split()[1])
            ALLOWED_USERS.add(new_id)
            bot.reply_to(message, f"✅ User `{new_id}` Added!")
        except: bot.reply_to(message, "Usage: `/add ID`")

# --- LOGIN FLOW ---
@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def login_init(message):
    user_sessions[message.chat.id] = {'v': message.text}
    bot.send_message(message.chat.id, "📧 Enter Game Email:", reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_pass)

def get_pass(message):
    user_sessions[message.chat.id]['email'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 Enter Game Password:")
    bot.register_next_step_handler(message, process_login)

def process_login(message):
    cid = message.chat.id
    session = user_sessions.get(cid)
    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS[session['v']]}"
    res = requests.post(url, json={"email": session['email'], "password": message.text.strip(), "returnSecureToken": True}).json()
    
    if 'idToken' in res:
        session.update({'token': res['idToken'], 'localid': res['localId']})
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            telebot.types.InlineKeyboardButton("🔓 UNLOCK EVERYTHING (ALL)", callback_data="all"),
            telebot.types.InlineKeyboardButton("💰 50M CASH + COINS", callback_data="money"),
            telebot.types.InlineKeyboardButton("🚀 W16 + EXTREME MODS", callback_data="mods"),
            telebot.types.InlineKeyboardButton("🏠 UNLOCK ALL HOUSES", callback_data="houses"),
            telebot.types.InlineKeyboardButton("🛞 PAID WHEELS", callback_data="wheels")
        )
        bot.send_message(cid, "✅ **Login Success!**\nഎല്ലാം അൺലോക്ക് ചെയ്യാൻ താഴെ സെലക്ട് ചെയ്യുക:", reply_markup=markup)
    else: bot.send_message(cid, "❌ Login Failed!")

# --- CALLBACKS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    if call.data == "all":
        data = {"money": 50000000, "coins": 45000, "w16_engine": 1, "all_horns": 1, "smoke_unlocked": 1, "houses_unlocked": 1, "all_wheels_unlocked": 1, "engine_damage": 0}
        msg = "✅ EVERYTHING UNLOCKED!"
    elif call.data == "money":
        data = {"money": 50000000, "coins": 45000}
        msg = "💰 Money & Coins Added!"
    elif call.data == "mods":
        data = {"w16_engine": 1, "all_horns": 1, "smoke_unlocked": 1, "engine_damage": 0}
        msg = "🚀 Mods Unlocked!"
    elif call.data == "houses":
        data = {"houses_unlocked": 1}
        msg = "🏠 Houses Unlocked!"
    elif call.data == "wheels":
        data = {"all_wheels_unlocked": 1}
        msg = "🛞 Wheels Unlocked!"
    
    resp = sync_data(cid, data)
    if resp.status_code == 200:
        bot.answer_callback_query(call.id, msg)
        bot.send_message(cid, f"{msg}\n\n⚠️ **ഗെയിം റീസ്റ്റാർട്ട് ചെയ്യുക, എന്നിട്ട് Settings-ൽ പോയി Sync/Save Online നൽകുക.**")
    else: bot.send_message(cid, "❌ Server Error!")

# --- STARTUP ---
if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling(none_stop=True)).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
