import telebot
import requests
from telebot import types
import json
from datetime import datetime
from threading import Thread
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 Flame Mega Tool is Online!"

# --- CONFIGURATION ---
TOKEN = "8494305163:AAFrXuG50xpdsYS0Jz-lFPk_tEjb3y5lpV0"
bot = telebot.TeleBot(TOKEN, threaded=False)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902} 

API_KEYS = {"CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM", 
            "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"}

user_sessions = {}

# --- HELPER: MASTER SYNC ---
def master_sync(cid, payload_data):
    session = user_sessions.get(cid)
    headers = {"Authorization": f"Bearer {session['token']}", "Content-Type": "application/json"}
    ts = int(datetime.now().timestamp()*1000)
    
    # നിങ്ങൾ ചോദിച്ച എല്ലാ ഐറ്റംസും ഉൾപ്പെടുത്തിയ മാസ്റ്റർ ലിസ്റ്റ്
    full_payload = {
        "localID": session['localid'],
        "Timestamp": ts
    }
    full_payload.update(payload_data)
    
    url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncData"
    return requests.post(url, headers=headers, json={"data": json.dumps(full_payload)})

# --- START & LOGIN (അതേപടി തുടരുന്നു) ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in ALLOWED_USERS:
        bot.send_message(uid, f"❌ No Access! ID: `{uid}`")
        return
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('CPM1', 'CPM2')
    bot.send_message(message.chat.id, "🏎️ **CPM MEGA UNLOCKER**\nSelect Version:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def login_init(message):
    user_sessions[message.chat.id] = {'v': message.text}
    bot.send_message(message.chat.id, "📧 Email?")
    bot.register_next_step_handler(message, get_pass)

def get_pass(message):
    user_sessions[message.chat.id]['email'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 Password?")
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
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("🔓 UNLOCK EVERYTHING (ALL)", callback_data="unlock_all"),
        types.InlineKeyboardButton("🚀 W16 + ENGINE FIX", callback_data="unlock_w16"),
        types.InlineKeyboardButton("🏠 UNLOCK HOUSES", callback_data="unlock_houses"),
        types.InlineKeyboardButton("🛞 PAID WHEELS", callback_data="unlock_wheels"),
        types.InlineKeyboardButton("💨 SMOKE & HORNS", callback_data="unlock_misc"),
        types.InlineKeyboardButton("💰 50M CASH + 50K COINS", callback_data="unlock_money")
    )
    bot.send_message(cid, "🔥 **FLAME MEGA MENU**\nഎല്ലാം അൺലോക്ക് ചെയ്യാൻ താഴെ സെലക്ട് ചെയ്യുക:", reply_markup=m)

# --- CALLBACK ACTIONS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    if call.data == "unlock_all":
        # ഇതാണ് മാസ്റ്റർ അൺലോക്കർ
        data = {
            "w16_engine": 1, "all_horns": 1, "smoke_unlocked": 1, 
            "all_wheels_unlocked": 1, "houses_unlocked": 1, "engine_damage": 0,
            "money": 50000000, "coins": 50000
        }
        master_sync(cid, data)
        bot.answer_callback_query(call.id, "✅ EVERYTHING UNLOCKED!")

    elif call.data == "unlock_w16":
        master_sync(cid, {"w16_engine": 1, "engine_damage": 0})
        bot.answer_callback_query(call.id, "🚀 W16 Unlocked!")

    elif call.data == "unlock_wheels":
        master_sync(cid, {"all_wheels_unlocked": 1})
        bot.answer_callback_query(call.id, "🛞 Paid Wheels Unlocked!")

    elif call.data == "unlock_houses":
        master_sync(cid, {"houses_unlocked": 1})
        bot.answer_callback_query(call.id, "🏠 All Houses Unlocked!")

    elif call.data == "unlock_misc":
        master_sync(cid, {"all_horns": 1, "smoke_unlocked": 1})
        bot.answer_callback_query(call.id, "💨 Smoke & Horns Unlocked!")

# --- RUN ---
if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling(none_stop=True)).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
