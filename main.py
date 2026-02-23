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
    return "🔥 Flame Bot: Protocol 10.1 Active"

TOKEN = "8494305163:AAFrXuG50xpdsYS0Jz-lFPk_tEjb3y5lpV0"
bot = telebot.TeleBot(TOKEN, threaded=False)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902} 

# ഒറിജിനൽ ഗെയിം API Keys
API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_sessions = {}

def master_inject(cid, data_payload):
    session_data = user_sessions.get(cid)
    
    # സെർവർ ലിങ്കുകൾ (നിർബന്ധമായും ശരിയായിരിക്കണം)
    if session_data['v'] == "CPM1":
        url = f"https://cp-multiplayer-default-rtdb.firebaseio.com/users/{session_data['localid']}.json"
    else:
        url = f"https://cpm-2-7cea1-default-rtdb.firebaseio.com/users/{session_data['localid']}.json"

    # ഒരു സെഷൻ ക്രിയേറ്റ് ചെയ്യുന്നു (ഇത് കണക്ഷൻ കട്ടാകുന്നത് ഒഴിവാക്കും)
    s = requests.Session()
    params = {"auth": session_data['token']}
    
    headers = {
        "User-Agent": "UnityPlayer/2019.4.31f1 (UnityWorks/1.0)",
        "Content-Type": "application/json",
        "Connection": "keep-alive"
    }

    try:
        # Patch ഉപയോഗിച്ച് ഡാറ്റ ഇൻജക്ട് ചെയ്യുന്നു
        response = s.patch(url, params=params, json=data_payload, headers=headers, timeout=15)
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

# --- ലോഗിൻ ഫ്ലോ ---
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id not in ALLOWED_USERS: return
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('CPM1', 'CPM2')
    bot.send_message(message.chat.id, "🏎️ **CPM FINAL PROTOCOL**\nSelect Version:", reply_markup=markup)

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
        m.add(telebot.types.InlineKeyboardButton("🔓 UNLOCK ALL (NO ERROR)", callback_data="final_all"))
        bot.send_message(cid, "✅ **READY!**", reply_markup=m)
    else:
        bot.send_message(cid, "❌ Login Failed!")

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    # എല്ലാ ഫീച്ചറുകളും ഒറ്റയടിക്ക്
    data = {
        "money": 50000000,
        "coins": 50000,
        "w16_engine": 1,
        "houses_unlocked": 1,
        "all_wheels_unlocked": 1,
        "sirens_unlocked": 1
    }
    
    resp = master_inject(cid, data)
    
    if resp and resp.status_code == 200:
        bot.answer_callback_query(call.id, "✅ SUCCESS!")
        bot.send_message(cid, "🎉 **Injected!**\nഗെയിം റീസ്റ്റാർട്ട് ചെയ്ത് **Sign In** ചെയ്യുക.")
    else:
        status = resp.status_code if resp else "Timeout"
        bot.send_message(cid, f"❌ Server Rejected ({status}).\n\n**കാരണം:** നിങ്ങളുടെ അക്കൗണ്ട് സെർവർ ബ്ലോക്ക് ചെയ്തിരിക്കാം അല്ലെങ്കിൽ ഈ ഇമെയിൽ നിലവിൽ ലോഗിൻ അല്ല.")

if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling(none_stop=True)).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
