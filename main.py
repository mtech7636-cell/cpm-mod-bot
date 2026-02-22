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
    return "🔥 Flame Mega Bot is Online!"

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
def sync_to_cpm(cid, data_payload):
    session = user_sessions.get(cid)
    headers = {
        "Authorization": f"Bearer {session['token']}",
        "Content-Type": "application/json",
        "User-Agent": "BestHTTP/2 v2.4.0"
    }
    ts = int(datetime.now().timestamp() * 1000)
    data_payload.update({"localID": session['localid'], "Timestamp": ts})
    
    url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncData"
    if session['v'] == "CPM2":
        url = "https://us-central1-cpm-2-7cea1.cloudfunctions.net/SyncData_AppI"
        
    return requests.post(url, headers=headers, json={"data": json.dumps(data_payload)})

# --- START & LOGIN ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in ALLOWED_USERS:
        bot.send_message(uid, f"❌ No Access! ID: `{uid}`")
        return
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('CPM1', 'CPM2')
    bot.send_message(message.chat.id, "🏎️ **CPM MEGA TOOL**\nVersion സെലക്ട് ചെയ്യുക:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def login_init(message):
    user_sessions[message.chat.id] = {'v': message.text}
    bot.send_message(message.chat.id, "📧 Email നൽകുക:", reply_markup=telebot.types.ReplyKeyboardRemove())
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
        show_main_menu(cid)
    else: bot.send_message(cid, "❌ Login Failed!")

# --- MENUS ---
def show_main_menu(cid):
    m = telebot.types.InlineKeyboardMarkup(row_width=2)
    m.add(
        telebot.types.InlineKeyboardButton("💰 MONEY & COINS", callback_data="m_money"),
        telebot.types.InlineKeyboardButton("🚀 EXTREME MODS", callback_data="m_mods"),
        telebot.types.InlineKeyboardButton("👑 RANK & UNLOCKS", callback_data="m_unlock"),
        telebot.types.InlineKeyboardButton("🔓 UNLOCK EVERYTHING", callback_data="all_in_one")
    )
    bot.send_message(cid, "🔥 **MAIN MENU**\nഒരു കാറ്റഗറി സെലക്ട് ചെയ്യുക:", reply_markup=m)

# --- CALLBACK HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    
    if call.data == "m_money":
        m = telebot.types.InlineKeyboardMarkup()
        m.add(telebot.types.InlineKeyboardButton("💵 50M CASH", callback_data="do_50m"),
              telebot.types.InlineKeyboardButton("🪙 50K COINS", callback_data="do_50k"))
        bot.edit_message_text("💰 **CASH & COINS MENU**", cid, call.message.message_id, reply_markup=m)

    elif call.data == "m_mods":
        m = telebot.types.InlineKeyboardMarkup()
        m.add(telebot.types.InlineKeyboardButton("🏎️ W16 ENGINE", callback_data="do_w16"),
              telebot.types.InlineKeyboardButton("💨 ALL SMOKE", callback_data="do_smoke"),
              telebot.types.InlineKeyboardButton("📯 ALL HORNS", callback_data="do_horns"),
              telebot.types.InlineKeyboardButton("🛠️ ENGINE FIX", callback_data="do_fix"))
        bot.edit_message_text("🚀 **EXTREME MODS MENU**", cid, call.message.message_id, reply_markup=m)

    elif call.data == "m_unlock":
        m = telebot.types.InlineKeyboardMarkup()
        m.add(telebot.types.InlineKeyboardButton("🏠 ALL HOUSES", callback_data="do_houses"),
              telebot.types.InlineKeyboardButton("🛞 PAID WHEELS", callback_data="do_wheels"),
              telebot.types.InlineKeyboardButton("👑 KING RANK", callback_data="do_rank"))
        bot.edit_message_text("🔓 **UNLOCKS MENU**", cid, call.message.message_id, reply_markup=m)

    # ACTIONS
    data = {}
    if call.data == "all_in_one":
        data = {"money": 50000000, "coins": 50000, "w16_engine": 1, "houses_unlocked": 1, "all_wheels_unlocked": 1, "all_horns": 1, "smoke_unlocked": 1, "engine_damage": 0}
    elif call.data == "do_50m": data = {"money": 50000000}
    elif call.data == "do_50k": data = {"coins": 50000}
    elif call.data == "do_w16": data = {"w16_engine": 1}
    elif call.data == "do_houses": data = {"houses_unlocked": 1}
    elif call.data == "do_wheels": data = {"all_wheels_unlocked": 1}
    elif call.data == "do_rank": data = {"race_win": 9999, "is_king": True} # Rank ലോജിക്
    
    if data:
        resp = sync_to_cpm(cid, data)
        if resp.status_code == 200:
            bot.answer_callback_query(call.id, "✅ SUCCESS!")
            bot.send_message(cid, "🚀 **Done!**\nഗെയിം ക്ലോസ് ചെയ്ത് **Clear Data** ചെയ്ത ശേഷം വീണ്ടും ലോഗിൻ ചെയ്യുക.")

# --- RUN ---
if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling(none_stop=True)).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
