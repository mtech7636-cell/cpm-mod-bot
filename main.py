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
    return "🔥 Flame Bot: Binary Sync v11 is Live"

TOKEN = "8494305163:AAFrXuG50xpdsYS0Jz-lFPk_tEjb3y5lpV0"
bot = telebot.TeleBot(TOKEN, threaded=False)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902} 

API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_sessions = {}

def binary_sync(cid, data_payload):
    session_data = user_sessions.get(cid)
    
    # CPM സെർവർ റൂട്ടുകൾ മാറ്റമില്ലാതെ നിലനിർത്തുന്നു
    if session_data['v'] == "CPM1":
        url = f"https://cp-multiplayer-default-rtdb.firebaseio.com/users/{session_data['localid']}.json"
    else:
        url = f"https://cpm-2-7cea1-default-rtdb.firebaseio.com/users/{session_data['localid']}.json"

    # ടൈംഔട്ട് ഒഴിവാക്കാൻ ഹെഡറുകൾ പരിഷ്കരിച്ചു
    headers = {
        "User-Agent": "UnityPlayer/2019.4.31f1 (UnityWorks/1.0)",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Firebase-ETag": "true"
    }
    
    params = {"auth": session_data['token']}

    try:
        # ഡാറ്റ ഇൻജക്ട് ചെയ്യാൻ PATCH ഉപയോഗിക്കുന്നു
        # ടൈംഔട്ട് പ്രശ്നം ഒഴിവാക്കാൻ stream=True നൽകുന്നു
        response = requests.patch(url, params=params, json=data_payload, headers=headers, timeout=25)
        return response
    except Exception as e:
        return None

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id not in ALLOWED_USERS: return
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('CPM1', 'CPM2')
    bot.send_message(message.chat.id, "🏎️ **CPM FINAL BYPASS**\nSelect Version:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def login_init(message):
    user_sessions[message.chat.id] = {'v': message.text}
    bot.send_message(message.chat.id, "📧 Email:")
    bot.register_next_step_handler(message, get_pass)

def get_pass(message):
    user_sessions[message.chat.id]['email'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 Password:")
    bot.register_next_step_handler(message, process_login)

def process_login(message):
    cid = message.chat.id
    sd = user_sessions.get(cid)
    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS[sd['v']]}"
    res = requests.post(url, json={"email": sd['email'], "password": message.text.strip(), "returnSecureToken": True}).json()
    
    if 'idToken' in res:
        sd.update({'token': res['idToken'], 'localid': res['localId']})
        m = telebot.types.InlineKeyboardMarkup()
        m.add(telebot.types.InlineKeyboardButton("🔓 FORCE SYNC EVERYTHING", callback_data="sync_all"))
        bot.send_message(cid, "✅ **READY!**", reply_markup=m)
    else:
        bot.send_message(cid, "❌ Login Failed!")

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    # ഡാറ്റാ ലോഡ്
    data = {
        "money": 50000000,
        "coins": 50000,
        "w16_engine": 1,
        "houses_unlocked": 1,
        "all_wheels_unlocked": 1,
        "all_horns": 1,
        "smoke_unlocked": 1,
        "sirens_unlocked": 1
    }
    
    resp = binary_sync(cid, data)
    
    if resp and resp.status_code == 200:
        bot.answer_callback_query(call.id, "✅ SUCCESS!")
        bot.send_message(cid, "🎉 **Success!**\nനിങ്ങളുടെ അക്കൗണ്ടിൽ എല്ലാം അപ്‌ഡേറ്റ് ആയി.\n\n**ഇനി ശ്രദ്ധിക്കൂ:**\nഫോണിൽ പോയി ഗെയിമിന്റെ **Clear Data** അടിക്കുക. എന്നിട്ട് ലോഗിൻ ചെയ്യുക. ഇപ്പോൾ ഉറപ്പായും വരും.")
    else:
        bot.send_message(cid, "❌ ഇപ്പോഴും കണക്ഷൻ കിട്ടുന്നില്ല. ഒരു പക്ഷേ നിങ്ങളുടെ അക്കൗണ്ട് CPM സെർവറിൽ നിന്ന് ബാൻ ചെയ്തിട്ടുണ്ടാകാം. പുതിയൊരു ഐഡി വെച്ച് ട്രൈ ചെയ്തു നോക്കൂ.")

if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling(none_stop=True)).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
