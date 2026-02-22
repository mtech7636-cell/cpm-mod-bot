import telebot
import requests
from telebot import types
import json
from datetime import datetime
from threading import Thread
from flask import Flask
import os

# --- FLASK FOR UPTIME ---
app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 Flame Bot is Live!"

# --- CONFIGURATION ---
TOKEN = "8494305163:AAFrXuG50xpdsYS0Jz-lFPk_tEjb3y5lpV0"
bot = telebot.TeleBot(TOKEN, threaded=False)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902} 

API_KEYS = {"CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM", 
            "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"}

user_sessions = {}

# --- ADMIN COMMANDS ---
@bot.message_handler(commands=['add'])
def add_user(message):
    if message.from_user.id == ADMIN_ID:
        try:
            target_id = int(message.text.split()[1])
            ALLOWED_USERS.add(target_id)
            bot.reply_to(message, f"✅ User `{target_id}` added.")
        except:
            bot.reply_to(message, "Usage: `/add ID`")

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in ALLOWED_USERS:
        bot.send_message(uid, f"⏳ Access ആവശ്യമുണ്ട്.\nYour ID: `{uid}`", parse_mode="Markdown")
        bot.send_message(ADMIN_ID, f"🔔 **New Request:** `{uid}`")
        return
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton('CPM1'), types.KeyboardButton('CPM2'))
    bot.send_message(message.chat.id, "🔥 **FLAME V22.6.1 FINAL**", reply_markup=markup)

# --- LOGIN & ACTIONS (FULL) ---
@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def login_init(message):
    if message.from_user.id not in ALLOWED_USERS: return
    user_sessions[message.chat.id] = {'v': message.text}
    bot.send_message(message.chat.id, "📧 Email നൽകുക:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_pass)

def get_pass(message):
    user_sessions[message.chat.id]['email'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 Password നൽകുക:")
    bot.register_next_step_handler(message, process_login)

def process_login(message):
    cid = message.chat.id
    pwd = message.text.strip()
    session = user_sessions.get(cid)
    try:
        url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS[session['v']]}"
        res = requests.post(url, json={"email": session['email'], "password": pwd, "returnSecureToken": True}).json()
        if 'idToken' in res:
            session.update({'token': res['idToken'], 'localid': res['localId']})
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("💰 50M CASH", callback_data="set_money"),
                types.InlineKeyboardButton("👑 KING RANK", callback_data="set_rank")
            )
            bot.send_message(cid, f"✅ **LOGIN SUCCESS!**", reply_markup=markup)
        else:
            bot.send_message(cid, "❌ Login Failed!")
    except:
        bot.send_message(cid, "❌ Error!")

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    session = user_sessions.get(cid)
    if not session: return
    headers = {"Authorization": f"Bearer {session['token']}", "Content-Type": "application/json"}
    ts = int(datetime.now().timestamp()*1000)

    if call.data == "set_money":
        url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncData"
        payload = {"data": json.dumps({"money": 50000000, "coins": 45000, "localID": session['localid'], "Timestamp": ts})}
        requests.post(url, headers=headers, json=payload)
        bot.answer_callback_query(call.id, "💰 Money Added!")

# --- THE FIX ---
def run_bot():
    bot.infinity_polling(none_stop=True)

if __name__ == "__main__":
    t = Thread(target=run_bot)
    t.daemon = True
    t.start()
    # Port must be bound to 0.0.0.0
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
