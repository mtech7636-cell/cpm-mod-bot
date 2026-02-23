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
    return "🔥 CPM Working Panel v14.0 Active"

TOKEN = "8494305163:AAFrXuG50xpdsYS0Jz-lFPk_tEjb3y5lpV0"
bot = telebot.TeleBot(TOKEN, threaded=False)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902} 

API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_sessions = {}

# --- WORKING SYNC FUNCTION ---
def apply_feature(cid, data_payload):
    sd = user_sessions.get(cid)
    base = "https://cp-multiplayer-default-rtdb.firebaseio.com" if sd['v'] == "CPM1" else "https://cpm-2-7cea1-default-rtdb.firebaseio.com"
    
    # User Profile path for Rank and Email
    url = f"{base}/users/{sd['localid']}.json?auth={sd['token']}"
    
    try:
        response = requests.patch(url, json=data_payload, timeout=20)
        return response.status_code == 200
    except:
        return False

# --- LOGIN FLOW ---
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id not in ALLOWED_USERS: return
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('CPM1', 'CPM2')
    bot.send_message(message.chat.id, "🏎️ **CPM WORKING TOOLS**\nSelect Version:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def login_init(message):
    user_sessions[message.chat.id] = {'v': message.text}
    bot.send_message(message.chat.id, "📧 Current Email:")
    bot.register_next_step_handler(message, get_pass)

def get_pass(message):
    user_sessions[message.chat.id]['email'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 Password:")
    bot.register_next_step_handler(message, process_login)

def process_login(message):
    cid = message.chat.id
    sd = user_sessions.get(cid)
    auth_url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS[sd['v']]}"
    res = requests.post(auth_url, json={"email": sd['email'], "password": message.text.strip(), "returnSecureToken": True}).json()
    
    if 'idToken' in res:
        sd.update({'token': res['idToken'], 'localid': res['localId']})
        m = telebot.types.InlineKeyboardMarkup(row_width=1)
        m.add(
            telebot.types.InlineKeyboardButton("👑 UNLOCK KING RANK", callback_data="set_king"),
            telebot.types.InlineKeyboardButton("📧 CHANGE EMAIL ID", callback_data="change_mail")
        )
        bot.send_message(cid, "✅ **Logged In Successfully!**", reply_markup=m)
    else:
        bot.send_message(cid, "❌ Login Failed!")

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    
    if call.data == "set_king":
        # King Rank data
        success = apply_feature(cid, {"rank": 1, "is_king": True})
        if success:
            bot.send_message(cid, "🎉 **King Rank Applied!**\nRestart and Sync.")
        else:
            bot.send_message(cid, "❌ Error applying rank.")

    elif call.data == "change_mail":
        bot.send_message(cid, "📝 Enter New Email ID:")
        bot.register_next_step_handler(call.message, do_email_change)

def do_email_change(message):
    cid = message.chat.id
    new_email = message.text.strip()
    # Firebase-ൽ ഇമെയിൽ മാറ്റുന്ന രീതി
    success = apply_feature(cid, {"email": new_email})
    if success:
        bot.send_message(cid, f"✅ **Email changed to:** `{new_email}`\nUse this to login next time.")
    else:
        bot.send_message(cid, "❌ Failed to change email.")

if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling(none_stop=True)).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
