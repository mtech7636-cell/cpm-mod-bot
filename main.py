import telebot
import requests
from telebot import types
import json
from datetime import datetime
from threading import Thread
from flask import Flask
import os

app = Flask('')

@app.route('/')
def home():
    return "🔥 Flame Bot V22.5 is Online & Running!"

def run_flask():
    # Render-ൽ റൺ ചെയ്യാൻ ആവശ്യമായ പോർട്ട് സെറ്റിംഗ്സ്
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURATION ---
TOKEN = "8314787817:AAHpZnchNnDOaLARhaVU6eNLGbyDuyjz-n0"
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=20)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902} # നിങ്ങളുടെ ഐഡി ബൈ ഡിഫോൾട്ട് ആഡ് ചെയ്തു

API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_sessions = {}

# --- START & APPROVAL ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in ALLOWED_USERS:
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ APPROVE USER", callback_data=f"approve_{uid}"))
        bot.send_message(ADMIN_ID, f"🔔 **NEW ACCESS REQUEST:** `{uid}`", reply_markup=markup)
        return bot.reply_to(message, "⏳ അഡ്മിൻ അപ്രൂവലിനായി കാത്തിരിക്കൂ. അഡ്മിൻ പെർമിഷൻ നൽകിയാൽ മാത്രമേ ഇത് ഉപയോഗിക്കാൻ കഴിയൂ.")
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton('CPM1'), types.KeyboardButton('CPM2'))
    bot.send_message(message.chat.id, "🔥 **CPM NOOB STYLE TOOLS**\nവേർഷൻ തിരഞ്ഞെടുക്കുക:", reply_markup=markup)

# --- LOGIN PROCESS ---
@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def login_init(message):
    user_sessions[message.chat.id] = {'v': message.text}
    bot.send_message(message.chat.id, f"✅ {message.text} Selected.\n📧 CPM Email നൽകുക:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_pass)

def get_pass(message):
    user_sessions[message.chat.id]['email'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 Password നൽകുക:")
    bot.register_next_step_handler(message, process_login)

def process_login(message):
    cid = message.chat.id
    pwd = message.text.strip()
    session = user_sessions.get(cid)
    bot.send_message(cid, "⏳ ലോഗിൻ ചെയ്യുന്നു... ദയവായി കാത്തിരിക്കുക.")

    def login_task():
        try:
            res = requests.post(f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS[session['v']]}", 
                               json={"email": session['email'], "password": pwd, "returnSecureToken": True}, timeout=15).json()
            if 'idToken' in res:
                user_sessions[cid].update({'token': res['idToken'], 'localid': res['localId'], 'pass': pwd})
                
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(
                    types.InlineKeyboardButton("👑 KING RANK (FULL)", callback_data="set_rank"),
                    types.InlineKeyboardButton("🔓 UNLOCK ALL CARS", callback_data="unlock_cars"),
                    types.InlineKeyboardButton("✨ CHROME PAINT ALL", callback_data="set_chrome"),
                    types.InlineKeyboardButton("💰 50M CASH + 45K COINS", callback_data="set_money"),
                    types.InlineKeyboardButton("📢 SIRENS & HORNS", callback_data="set_siren"),
                    types.InlineKeyboardButton("🛠️ FIX ENGINE & INF FUEL", callback_data="set_mods")
                )
                bot.send_message(cid, f"✅ **LOGIN SUCCESS!**\nWelcome: {session['email']}", reply_markup=markup)
            else:
                bot.send_message(cid, "❌ Login Failed! Email അല്ലെങ്കിൽ Password തെറ്റാണ്.")
        except:
            bot.send_message(cid, "❌ സർവർ ബിസിയാണ്. അല്പസമയത്തിന് ശേഷം വീണ്ടും ശ്രമിക്കൂ.")

    Thread(target=login_task).start()

# --- CALLBACK HANDLERS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    
    # അപ്രൂവൽ ലോജിക്
    if call.data.startswith("approve_"):
        new_u = int(call.data.split("_")[1])
        ALLOWED_USERS.add(new_u)
        bot.send_message(new_u, "🎉 അഡ്മിൻ നിങ്ങളെ അപ്രൂവ് ചെയ്തു! ഇനി /start അമർത്തുക.")
        bot.answer_callback_query(call.id, "User Approved!")
        return

    session = user_sessions.get(cid)
    if not session or 'token' not in session: return

    headers = {"Authorization": f"Bearer {session['token']}", "Content-Type": "application/json"}
    ts = int(datetime.now().timestamp()*1000)

    # 1. King Rank
    if call.data == "set_rank":
        url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SetUserRating4" if session['v']=="CPM1" else "https://us-central1-cpm-2-7cea1.cloudfunctions.net/SetUserRating17_AppI"
        payload = {"data": json.dumps({"RatingData": {"time": 0.5, "race_win": 9999, "cars": 150}, "Timestamp": ts})}
        requests.post(url, headers=headers, json=payload)
        bot.send_message(cid, "👑 **King Rank Applied!**")

    # 2. Unlock All Cars (Noob Style)
    elif call.data == "unlock_cars":
        url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncData"
        payload = {"data": json.dumps({"all_cars_bought": True, "localID": session['localid'], "Timestamp": ts})}
        requests.post(url, headers=headers, json=payload)
        bot.send_message(cid, "🔓 **All Cars Unlocked!** (ഗെയിം റീസ്റ്റാർട്ട് ചെയ്യുക)")

    # 3. Chrome Paint
    elif call.data == "set_chrome":
        url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncData"
        payload = {"data": json.dumps({"is_chrome": True, "localID": session['localid'], "Timestamp": ts})}
        requests.post(url, headers=headers, json=payload)
        bot.send_message(cid, "✨ **Chrome Effect Added!**")

    # 4. Money & Coins
    elif call.data == "set_money":
        url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncData"
        payload = {"data": json.dumps({"money": 50000000, "coins": 45000, "localID": session['localid'], "Timestamp": ts})}
        requests.post(url, headers=headers, json=payload)
        bot.send_message(cid, "💰 **50M Cash & 45K Coins Added!**")

# --- START SERVER ---
if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling()
