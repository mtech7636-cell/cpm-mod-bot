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
def home(): return "🔥 CPM1 MASTER BOT ONLINE"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

TOKEN = "8314787817:AAHpZnchNnDOaLARhaVU6eNLGbyDuyjz-n0"
bot = telebot.TeleBot(TOKEN, threaded=True)

ADMIN_ID = 7212602902
KEY_FILE = "keys.txt"

# CPM1 New Endpoint API Key
API_KEY_CPM1 = "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM"

user_sessions = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔑 LOGIN WITH KEY", callback_data="login_start"))
    bot.send_message(message.chat.id, "🏁 **CPM1 LATEST TOOLS (V4.8.x)**\n\nഈ വേർഷനിൽ 50M പണം ഉറപ്പായും ആഡ് ആകും.", reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['genkey'])
def genkey_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    new_key = "BM-" + ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=12))
    with open(KEY_FILE, "a") as f: f.write(f"{new_key}|LIFETIME\n")
    bot.reply_to(message, f"✅ **Key:** `{new_key}`")

@bot.message_handler(func=lambda m: m.text.startswith("BM-"))
def verify_key(message):
    found = False
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            if message.text.strip().upper() in f.read(): found = True
    
    if found:
        user_sessions[message.chat.id] = {'auth': True}
        bot.send_message(message.chat.id, "✅ Key Verified! ഇനി **Email** നൽകുക:")
        bot.register_next_step_handler(message, get_email)
    else:
        bot.reply_to(message, "❌ Invalid Key!")

def get_email(message):
    user_sessions[message.chat.id]['email'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 **Password** നൽകുക:")
    bot.register_next_step_handler(message, get_password)

def get_password(message):
    pwd = message.text.strip()
    cid = message.chat.id
    session = user_sessions.get(cid)
    bot.send_message(cid, "⏳ Connecting to CPM1 Server...")

    def login_task():
        try:
            res = requests.post(f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEY_CPM1}", 
                               json={"email": session['email'], "password": pwd, "returnSecureToken": True}).json()
            if 'idToken' in res:
                user_sessions[cid].update({'token': res['idToken'], 'localid': res['localId']})
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("💰 ADD 50,000,000 CASH", callback_data="add_money_pro"))
                bot.send_message(cid, f"✅ LOGIN SUCCESS!\nഇപ്പോൾ ബട്ടൺ അമർത്തുക.", reply_markup=markup)
            else:
                bot.send_message(cid, "❌ Login Failed!")
        except:
            bot.send_message(cid, "❌ Connection Error!")
    Thread(target=login_task).start()

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    bot.answer_callback_query(call.id)
    session = user_sessions.get(cid)

    if call.data == "add_money_pro":
        if not session or 'token' not in session: return
        
        headers = {"Authorization": f"Bearer {session['token']}", "Content-Type": "application/json"}
        ts = int(datetime.datetime.now().timestamp() * 1000)
        
        # പണം ഉറപ്പായും വരാൻ രണ്ട് വ്യത്യസ്ത മെത്തേഡുകൾ ഒരുമിച്ച് അയക്കുന്നു
        urls = [
            "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncUser2",
            "https://us-central1-cp-multiplayer.cloudfunctions.net/SetAppData"
        ]
        
        data_payload = {
            "data": json.dumps({
                "money": 50000000,
                "coins": 45000,
                "localID": session['localid'],
                "Timestamp": ts
            })
        }
        
        success_count = 0
        for url in urls:
            r = requests.post(url, headers=headers, json=data_payload)
            if r.status_code == 200: success_count += 1

        if success_count > 0:
            bot.send_message(cid, "✅ **CASH ADDED SUCCESSFULLY!**\n\n🛑 **നിങ്ങൾ ഇപ്പോൾ ചെയ്യേണ്ടത്:**\n1. ഗെയിം ക്ലോസ് ചെയ്യുക.\n2. CPM ആപ്പിന്റെ **Cache ക്ലിയർ ചെയ്യുക**.\n3. ഇന്റർനെറ്റ് ഓഫ് ചെയ്ത് ഗെയിം ഓൺ ചെയ്യുക, ലോഡ് ആയ ശേഷം നെറ്റ് ഓൺ ചെയ്യുക.\n4. പണം വന്നില്ലെങ്കിൽ മാത്രം ലോഗൗട്ട് ചെയ്ത് ഒന്നുകൂടി കയറുക.")
        else:
            bot.send_message(cid, "❌ സെർവർ തിരക്കിലാണ്. 1 മിനിറ്റ് കഴിഞ്ഞ് നോക്കൂ.")

if __name__ == "__main__":
    if not os.path.exists(KEY_FILE): open(KEY_FILE, "w").close()
    Thread(target=run_flask).start()
    bot.infinity_polling()
