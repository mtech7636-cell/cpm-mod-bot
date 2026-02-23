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
    return "🔥 Flame Ultimate Panel: Firebase Mode"

TOKEN = "8494305163:AAFrXuG50xpdsYS0Jz-lFPk_tEjb3y5lpV0"
bot = telebot.TeleBot(TOKEN, threaded=False)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902} 

API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_sessions = {}

# --- NEW DIRECT FIREBASE INJECTION ---
def inject_firebase(cid, data_payload):
    session = user_sessions.get(cid)
    
    # CPM സെർവറുകൾ ഇപ്പോൾ ഉപയോഗിക്കുന്ന ഡയറക്ട് ഫയർബേസ് ലിങ്കുകൾ
    if session['v'] == "CPM1":
        url = f"https://cp-multiplayer-default-rtdb.firebaseio.com/users/{session['localid']}.json?auth={session['token']}"
    else:
        url = f"https://cpm-2-7cea1-default-rtdb.firebaseio.com/users/{session['localid']}.json?auth={session['token']}"

    # സെർവർ ബ്ലോക്ക് ചെയ്യാതിരിക്കാൻ 'PATCH' മെത്തേഡ് ഉപയോഗിക്കുന്നു
    # ഇത് നിലവിലുള്ള ഡാറ്റ മാറ്റാതെ പുതിയത് ആഡ് ചെയ്യും
    try:
        response = requests.patch(url, json=data_payload, timeout=30)
        return response
    except:
        return None

# --- LOGIN & MENU ---
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id not in ALLOWED_USERS: return
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('CPM1', 'CPM2')
    bot.send_message(message.chat.id, "🏎️ **CPM FIREBASE PANEL v9.0**", reply_markup=markup)

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
    api_key = API_KEYS[session['v']]
    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={api_key}"
    res = requests.post(url, json={"email": session['email'], "password": message.text.strip(), "returnSecureToken": True}).json()
    
    if 'idToken' in res:
        session.update({'token': res['idToken'], 'localid': res['localId']})
        m = telebot.types.InlineKeyboardMarkup(row_width=2)
        m.add(
            telebot.types.InlineKeyboardButton("💵 50M CASH", callback_data="f_cash"),
            telebot.types.InlineKeyboardButton("🚀 W16 ENGINE", callback_data="f_w16"),
            telebot.types.InlineKeyboardButton("🏠 ALL HOUSES", callback_data="f_houses"),
            telebot.types.InlineKeyboardButton("🛞 ALL WHEELS", callback_data="f_wheels"),
            telebot.types.InlineKeyboardButton("🔓 UNLOCK ALL", callback_data="f_all")
        )
        bot.send_message(cid, "✅ **SYSTEM CONNECTED!**", reply_markup=m)
    else: bot.send_message(cid, "❌ Login Failed!")

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    data = {}
    
    if call.data == "f_all":
        data = {"money": 50000000, "coins": 50000, "w16_engine": 1, "houses_unlocked": 1, "all_wheels_unlocked": 1}
    elif call.data == "f_cash": data = {"money": 50000000}
    elif call.data == "f_w16": data = {"w16_engine": 1}

    resp = inject_firebase(cid, data)
    
    if resp and resp.status_code == 200:
        bot.answer_callback_query(call.id, "✅ SUCCESS!")
        bot.send_message(cid, "🎉 **Injected Successfully!**\nഗെയിം റീസ്റ്റാർട്ട് ചെയ്ത് ലോഗിൻ ചെയ്യുക.")
    else:
        bot.send_message(cid, "❌ Connection Error! ഒന്നുകൂടി ശ്രമിക്കൂ.")

if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling(none_stop=True)).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
