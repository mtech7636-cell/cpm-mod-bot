import telebot
import requests
from telebot import types
import json
import random
import datetime
from threading import Thread
from flask import Flask
import os

app = Flask('')
@app.route('/')
def home():
    return "🔥 CPM1 Fixed Bot is Online!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

TOKEN = "8314787817:AAHpZnchNnDOaLARhaVU6eNLGbyDuyjz-n0"
bot = telebot.TeleBot(TOKEN, threaded=True)

ADMIN_ID = 7212602902
KEY_FILE = "keys.txt"

# CPM1-ന്റെ ഏറ്റവും പുതിയ API Key
API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_sessions = {}

def save_key(key, expiry):
    with open(KEY_FILE, "a") as f:
        f.write(f"{key}|{expiry}\n")

def check_valid_key(key_input):
    if not os.path.exists(KEY_FILE): return False
    with open(KEY_FILE, "r") as f:
        for line in f:
            if key_input in line: return True
    return False

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔑 LOGIN WITH KEY", callback_data="login_start"))
    bot.send_message(message.chat.id, "🏁 **CPM1 FAST TOOLS**\n\nKey നൽകി ലോഗിൻ ചെയ്യുക.", reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['genkey'])
def genkey_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    new_key = "BM-" + ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=12))
    save_key(new_key, "LIFETIME")
    bot.reply_to(message, f"✅ **Key:** `{new_key}`")

@bot.message_handler(func=lambda m: m.text.startswith("BM-"))
def verify_key(message):
    if check_valid_key(message.text.strip().upper()):
        user_sessions[message.chat.id] = {'auth': True}
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add('CPM1', 'CPM2')
        bot.send_message(message.chat.id, "✅ Key OK! Version തിരഞ്ഞെടുക്കുക:", reply_markup=markup)
    else:
        bot.reply_to(message, "❌ Invalid Key!")

@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def get_version(message):
    cid = message.chat.id
    user_sessions[cid]['v'] = message.text
    bot.send_message(cid, f"📧 {message.text} Email നൽകുക:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_email)

def get_email(message):
    user_sessions[message.chat.id]['email'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 Password നൽകുക:")
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
                    types.InlineKeyboardButton("💰 ADD 50M & 45K COINS", callback_data="set_money"),
                    types.InlineKeyboardButton("👑 SET KING RANK", callback_data="set_rank")
                )
                bot.send_message(cid, f"✅ ലോഗിൻ വിജയിച്ചു!", reply_markup=markup)
            else:
                bot.send_message(cid, "❌ ലോഗിൻ പരാജയപ്പെട്ടു!")
        except:
            bot.send_message(cid, "❌ സർവർ കണക്ഷൻ എറർ!")
    Thread(target=login_task).start()

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    bot.answer_callback_query(call.id)
    session = user_sessions.get(cid)

    if not session or 'token' not in session: return

    headers = {"Authorization": f"Bearer {session['token']}", "Content-Type": "application/json"}
    
    # CPM1-ന് വേണ്ടിയുള്ള ലേറ്റസ്റ്റ് സർവർ എൻഡ്പോയിന്റ്
    if call.data == "set_money":
        url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncUser2"
        # CPM1 സെക്യൂരിറ്റി മറികടക്കാൻ കൂടുതൽ ഡാറ്റ ഉൾപ്പെടുത്തുന്നു
        payload = {
            "data": json.dumps({
                "money": 50000000,
                "coins": 45000,
                "localID": session['localid'],
                "Timestamp": int(datetime.datetime.now().timestamp() * 1000)
            })
        }
        res = requests.post(url, headers=headers, json=payload)
        
        if res.status_code == 200:
            bot.send_message(cid, "✅ **CPM1: 50M Added!**\n\n**പ്രധാന നിർദ്ദേശം:**\nഗെയിം ഇപ്പോൾ തന്നെ ക്ലോസ് ചെയ്യുക. എന്നിട്ട് സെറ്റിംഗ്‌സിൽ പോയി **Clear Cache** അടിച്ച് ലോഗിൻ ചെയ്യുക. എങ്കിൽ മാത്രമേ പണം വരൂ.")
        else:
            bot.send_message(cid, "❌ സർവർ സിങ്കിംഗ് പരാജയപ്പെട്ടു. അല്പം കഴിഞ്ഞ് നോക്കൂ.")

if __name__ == "__main__":
    if not os.path.exists(KEY_FILE): open(KEY_FILE, "w").close()
    Thread(target=run_flask).start()
    bot.infinity_polling()
