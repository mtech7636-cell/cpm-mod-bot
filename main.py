import telebot
import requests
from telebot import types
import json
from datetime import datetime
from threading import Thread
from flask import Flask
import os
import random

app = Flask('')

@app.route('/')
def home():
    return "🔥 CPM ULTIMATE BOT is Online & Running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURATION ---
# നിന്റെ ടോക്കൺ താഴെ ആഡ് ചെയ്തിട്ടുണ്ട്
TOKEN = "8314787817:AAHpZnchNnDOaLARhaVU6eNLGbyDuyjz-n0"
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=20)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902}

API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_sessions = {}

# --- UTILS (Rainbow Name Generator) ---
def get_rainbow_name(name):
    modified_name = ""
    for char in name:
        color = "%06x" % random.randint(0, 0xFFFFFF)
        modified_name += f"[{color}]{char}"
    return modified_name

# --- START & APPROVAL ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in ALLOWED_USERS:
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ APPROVE USER", callback_data=f"approve_{uid}"))
        bot.send_message(ADMIN_ID, f"🔔 **NEW ACCESS REQUEST:** `{uid}`", reply_markup=markup)
        return bot.reply_to(message, "⏳ അഡ്മിൻ അപ്രൂവലിനായി കാത്തിരിക്കൂ.")
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton('CPM1'), types.KeyboardButton('CPM2'))
    bot.send_message(message.chat.id, "🔥 **CPM ULTIMATE TOOLS**\nവേർഷൻ തിരഞ്ഞെടുക്കുക:", reply_markup=markup)

# --- LOGIN PROCESS ---
@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def login_init(message):
    user_sessions[message.chat.id] = {'v': message.text}
    bot.send_message(message.chat.id, f"✅ {message.text} Selected.\n📧 Email നൽകുക:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_pass)

def get_pass(message):
    user_sessions[message.chat.id]['email'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 Password നൽകുക:")
    bot.register_next_step_handler(message, process_login)

def process_login(message):
    cid = message.chat.id
    pwd = message.text.strip()
    session = user_sessions.get(cid)
    bot.send_message(cid, "⏳ ലോഗിൻ ചെയ്യുന്നു...")

    def login_task():
        try:
            res = requests.post(f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS[session['v']]}", 
                               json={"email": session['email'], "password": pwd, "returnSecureToken": True}, timeout=15).json()
            if 'idToken' in res:
                user_sessions[cid].update({'token': res['idToken'], 'localid': res['localId'], 'pass': pwd})
                
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    types.InlineKeyboardButton("👑 KING RANK", callback_data="set_rank"),
                    types.InlineKeyboardButton("🔓 UNLOCK ALL", callback_data="unlock_cars"),
                    types.InlineKeyboardButton("💰 50M & 45K", callback_data="set_money"),
                    types.InlineKeyboardButton("🌈 RAINBOW NAME", callback_data="rainbow_prompt"),
                    types.InlineKeyboardButton("🏠 HOUSE 3", callback_data="set_house"),
                    types.InlineKeyboardButton("💨 SMOKE", callback_data="set_smoke"),
                    types.InlineKeyboardButton("📢 SIRENS", callback_data="set_siren"),
                    types.InlineKeyboardButton("🚫 DEL FRIENDS", callback_data="del_friends")
                )
                bot.send_message(cid, f"✅ **SUCCESS!**\nWelcome: {session['email']}", reply_markup=markup)
            else:
                bot.send_message(cid, "❌ Login Failed! Email/Password തെറ്റാണ്.")
        except:
            bot.send_message(cid, "❌ സർവർ ബിസിയാണ്.")

    Thread(target=login_task).start()

# --- CALLBACK HANDLERS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    session = user_sessions.get(cid)

    if call.data.startswith("approve_"):
        new_u = int(call.data.split("_")[1])
        ALLOWED_USERS.add(new_u)
        bot.send_message(new_u, "🎉 അഡ്മിൻ നിങ്ങളെ അപ്രൂവ് ചെയ്തു! /start അടിക്കുക.")
        bot.answer_callback_query(call.id, "User Approved!")
        return

    if not session or 'token' not in session: return
    headers = {"Authorization": f"Bearer {session['token']}", "Content-Type": "application/json"}
    ts = int(datetime.now().timestamp()*1000)

    # King Rank
    if call.data == "set_rank":
        url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SetUserRating4" if session['v']=="CPM1" else "https://us-central1-cpm-2-7cea1.cloudfunctions.net/SetUserRating17_AppI"
        payload = {"data": json.dumps({"RatingData": {"race_win": 9999, "cars": 150}, "Timestamp": ts})}
        requests.post(url, headers=headers, json=payload)
        bot.send_message(cid, "👑 **King Rank Applied!**")

    # Money & Coins
    elif call.data == "set_money":
        url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncData"
        payload = {"data": json.dumps({"money": 50000000, "coin": 45000, "localID": session['localid'], "Timestamp": ts})}
        requests.post(url, headers=headers, json=payload)
        bot.send_message(cid, "💰 **Money & Coins Added!**")

    # Rainbow Name Prompt
    elif call.data == "rainbow_prompt":
        bot.send_message(cid, "🌈 Rainbow ആക്കേണ്ട പേര് അയക്കുക:")
        bot.register_next_step_handler(call.message, apply_rainbow)

    # House 3
    elif call.data == "set_house":
        url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncData"
        payload = {"data": json.dumps({"house3_bought": True, "localID": session['localid'], "Timestamp": ts})}
        requests.post(url, headers=headers, json=payload)
        bot.send_message(cid, "🏠 **House 3 Unlocked!**")

    # Unlock Cars
    elif call.data == "unlock_cars":
        url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncData"
        payload = {"data": json.dumps({"all_cars_bought": True, "localID": session['localid'], "Timestamp": ts})}
        requests.post(url, headers=headers, json=payload)
        bot.send_message(cid, "🔓 **All Cars Unlocked!**")

# Rainbow Name Implementation
def apply_rainbow(message):
    cid = message.chat.id
    session = user_sessions.get(cid)
    rainbow_name = get_rainbow_name(message.text)
    url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncData"
    payload = {"data": json.dumps({"Name": rainbow_name, "localID": session['localid'], "Timestamp": int(datetime.now().timestamp()*1000)})}
    headers = {"Authorization": f"Bearer {session['token']}", "Content-Type": "application/json"}
    requests.post(url, headers=headers, json=payload)
    bot.send_message(cid, f"✅ Rainbow Name Set: `{rainbow_name}`", parse_mode="Markdown")

# --- START SERVER ---
if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling()
