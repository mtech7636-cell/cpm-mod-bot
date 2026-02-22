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
    return "🔥 Flame Full Panel is Online!"

TOKEN = "8494305163:AAFrXuG50xpdsYS0Jz-lFPk_tEjb3y5lpV0"
bot = telebot.TeleBot(TOKEN, threaded=False)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902} 

API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_sessions = {}

# --- MASTER SYNC FUNCTION ---
def sync_action(cid, data_payload, endpoint_type="SyncData"):
    session = user_sessions.get(cid)
    headers = {
        "Authorization": f"Bearer {session['token']}",
        "Content-Type": "application/json",
        "User-Agent": "BestHTTP/2 v2.4.0"
    }
    ts = int(datetime.now().timestamp() * 1000)
    data_payload.update({"localID": session['localid'], "Timestamp": ts})
    
    # URL Selection to avoid 404
    base_url = "https://us-central1-cp-multiplayer.cloudfunctions.net/"
    if session['v'] == "CPM2":
        base_url = "https://us-central1-cpm-2-7cea1.cloudfunctions.net/"
        endpoint_type = "SyncData_AppI" if endpoint_type == "SyncData" else endpoint_type

    url = f"{base_url}{endpoint_type}"
    return requests.post(url, headers=headers, json={"data": json.dumps(data_payload)})

# --- START & LOGIN ---
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id not in ALLOWED_USERS: return
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('CPM1', 'CPM2')
    bot.send_message(message.chat.id, "🏎️ **CPM FULL MOD PANEL**\nSelect Version:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def login_init(message):
    user_sessions[message.chat.id] = {'v': message.text}
    bot.send_message(message.chat.id, "📧 Email:")
    bot.register_next_step_handler(message, get_pass)

def get_pass(message):
    user_sessions[message.chat.id]['email'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 Password:")
    bot.register_next_step_handler(message, process_login)

def process_login(message):
    cid = message.chat.id
    session = user_sessions.get(cid)
    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS[session['v']]}"
    res = requests.post(url, json={"email": session['email'], "password": message.text.strip(), "returnSecureToken": True}).json()
    if 'idToken' in res:
        session.update({'token': res['idToken'], 'localid': res['localId']})
        show_mega_menu(cid)
    else: bot.send_message(cid, "❌ Login Failed!")

# --- MEGA MENU ---
def show_mega_menu(cid):
    m = telebot.types.InlineKeyboardMarkup(row_width=2)
    m.add(
        telebot.types.InlineKeyboardButton("💵 50M CASH", callback_data="f_cash"),
        telebot.types.InlineKeyboardButton("🪙 50K COINS", callback_data="f_coins"),
        telebot.types.InlineKeyboardButton("🚀 W16 ENGINE", callback_data="f_w16"),
        telebot.types.InlineKeyboardButton("👑 KING RANK", callback_data="f_rank"),
        telebot.types.InlineKeyboardButton("🏠 ALL HOUSES", callback_data="f_houses"),
        telebot.types.InlineKeyboardButton("🛞 ALL WHEELS", callback_data="f_wheels"),
        telebot.types.InlineKeyboardButton("💨 ALL SMOKE", callback_data="f_smoke"),
        telebot.types.InlineKeyboardButton("📯 ALL HORNS", callback_data="f_horns"),
        telebot.types.InlineKeyboardButton("🚨 SIRENS UNLOCK", callback_data="f_sirens"),
        telebot.types.InlineKeyboardButton("🛠️ FIX ENGINE", callback_data="f_fix"),
        telebot.types.InlineKeyboardButton("📛 CHANGE NAME", callback_data="f_name"),
        telebot.types.InlineKeyboardButton("🔓 UNLOCK ALL", callback_data="f_all")
    )
    bot.send_message(cid, "🌟 **NOOB-GAMING PANEL FEATURES**", reply_markup=m)

# --- CALLBACKS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    cb = call.data
    
    actions = {
        "f_cash": {"money": 50000000},
        "f_coins": {"coins": 50000},
        "f_w16": {"w16_engine": 1},
        "f_houses": {"houses_unlocked": 1},
        "f_wheels": {"all_wheels_unlocked": 1},
        "f_smoke": {"smoke_unlocked": 1},
        "f_horns": {"all_horns": 1},
        "f_sirens": {"sirens_unlocked": 1},
        "f_fix": {"engine_damage": 0},
        "f_all": {"money": 50000000, "coins": 50000, "w16_engine": 1, "houses_unlocked": 1, "all_wheels_unlocked": 1, "smoke_unlocked": 1, "all_horns": 1, "sirens_unlocked": 1}
    }

    if cb == "f_name":
        bot.send_message(cid, "📛 പുതിയ പേര് നൽകുക:")
        bot.register_next_step_handler(call.message, lambda m: sync_action(cid, {"name": m.text.strip()}))
        return

    if cb in actions:
        resp = sync_action(cid, actions[cb])
        if resp.status_code == 200:
            bot.answer_callback_query(call.id, "✅ Done!")
        else:
            bot.send_message(cid, f"❌ Error: {resp.status_code}")

if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling(none_stop=True)).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
