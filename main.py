import telebot
import requests
from telebot import types
import json
import random
import datetime
from threading import Thread
from flask import Flask
import os

# --- FLASK FOR HOSTING ---
app = Flask('')
@app.route('/')
def home():
    return "🔥 Flame CPM Bot is Online!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- BOT CONFIGURATION ---
TOKEN = "8314787817:AAHpZnchNnDOaLARhaVU6eNLGbyDuyjz-n0"
bot = telebot.TeleBot(TOKEN, threaded=True)

ADMIN_ID = 7212602902
KEY_FILE = "keys.txt"

# API Keys for CPM Versions
API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_sessions = {}

# --- HELPER FUNCTIONS ---
def save_key(key, expiry):
    with open(KEY_FILE, "a") as f:
        f.write(f"{key}|{expiry}\n")

def check_valid_key(key_input):
    if not os.path.exists(KEY_FILE): return False
    with open(KEY_FILE, "r") as f:
        for line in f:
            if key_input in line: return True
    return False

# --- COMMANDS ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔑 ENTER KEY / LOGIN", callback_data="login_start"))
    
    if uid == ADMIN_ID:
        markup.add(types.InlineKeyboardButton("🛠 ADMIN: GEN KEY", callback_data="admin_gen"))
    
    bot.send_message(uid, "🏁 **CPM BLACK MARKET TOOLS**\n\nതുടങ്ങാൻ താഴെ ഉള്ള ബട്ടൺ അമർത്തി നിങ്ങളുടെ Key നൽകുക.", reply_markup=markup, parse_mode='Markdown')

# --- ADMIN GEN KEY ---
@bot.message_handler(commands=['genkey'])
def genkey_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_key = "BM-" + ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=12))
        save_key(new_key, "LIFETIME")
        bot.reply_to(message, f"✅ **New Key Created:** `{new_key}`")
    except: pass

# --- KEY & LOGIN LOGIC ---
@bot.message_handler(func=lambda m: m.text.startswith("BM-"))
def verify_and_start(message):
    if check_valid_key(message.text.strip()):
        user_sessions[message.chat.id] = {'auth': True}
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add('CPM1', 'CPM2')
        bot.send_message(message.chat.id, "✅ **Key Verified!**\nഇനി ഗെയിം വേർഷൻ തിരഞ്ഞെടുക്കുക:", reply_markup=markup)
    else:
        bot.reply_to(message, "❌ തെറ്റായ Key!")

@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def get_version(message):
    if message.chat.id in user_sessions and user_sessions[message.chat.id].get('auth'):
        user_sessions[message.chat.id]['v'] = message.text
        bot.send_message(message.chat.id, "📧 ഇനി നിങ്ങളുടെ CPM **Email** നൽകുക:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_email)

def get_email(message):
    user_sessions[message.chat.id]['email'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 ഇനി നിങ്ങളുടെ **Password** നൽകുക:")
    bot.register_next_step_handler(message, get_password)

def get_password(message):
    pwd = message.text.strip()
    cid = message.chat.id
    session = user_sessions.get(cid)
    bot.send_message(cid, "⏳ ലോഗിൻ ചെയ്യുന്നു...")

    def login_task():
        try:
            res = requests.post(f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS[session['v']]}", 
                               json={"email": session['email'], "password": pwd, "returnSecureToken": True}).json()
            if 'idToken' in res:
                user_sessions[cid].update({'token': res['idToken'], 'localid': res['localId']})
                
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(
                    types.InlineKeyboardButton("👑 KING RANK", callback_data="set_rank"),
                    types.InlineKeyboardButton("💰 50M CASH + 45K COINS", callback_data="set_money"),
                    types.InlineKeyboardButton("🔓 UNLOCK ALL CARS", callback_data="set_unlock"),
                    types.InlineKeyboardButton("✨ CHROME PAINT", callback_data="set_chrome")
                )
                bot.send_message(cid, f"✅ **LOGIN SUCCESS!**\nWelcome: {session['email']}", reply_markup=markup)
            else:
                bot.send_message(cid, "❌ ലോഗിൻ പരാജയപ്പെട്ടു!")
        except:
            bot.send_message(cid, "❌ സർവർ എറർ!")
    Thread(target=login_task).start()

# --- CALLBACKS FOR TOOLS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    session = user_sessions.get(cid)
    
    if call.data == "admin_gen":
        bot.send_message(cid, "കീ ഉണ്ടാക്കാൻ `/genkey` എന്ന് ടൈപ്പ് ചെയ്യുക.")
        return

    if not session or 'token' not in session: return

    headers = {"Authorization": f"Bearer {session['token']}", "Content-Type": "application/json"}
    ts = int(datetime.datetime.now().timestamp()*1000)

    if call.data == "set_rank":
        url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SetUserRating4" if session['v']=="CPM1" else "https://us-central1-cpm-2-7cea1.cloudfunctions.net/SetUserRating17_AppI"
        payload = {"data": json.dumps({"RatingData": {"time": 0.5, "race_win": 9999, "cars": 150}, "Timestamp": ts})}
        requests.post(url, headers=headers, json=payload)
        bot.send_message(cid, "👑 **King Rank Applied!**")

    elif call.data == "set_money":
        url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncData"
        payload = {"data": json.dumps({"money": 50000000, "coins": 45000, "localID": session['localid'], "Timestamp": ts})}
        requests.post(url, headers=headers, json=payload)
        bot.send_message(cid, "💰 **50M Cash & 45K Coins Added!**")

    elif call.data == "set_unlock":
        url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncData"
        payload = {"data": json.dumps({"all_cars_bought": True, "localID": session['localid'], "Timestamp": ts})}
        requests.post(url, headers=headers, json=payload)
        bot.send_message(cid, "🔓 **All Cars Unlocked!**")

# --- START SERVER ---
if __name__ == "__main__":
    if not os.path.exists(KEY_FILE): open(KEY_FILE, "w").close()
    Thread(target=run_flask).start()
    bot.infinity_polling()
