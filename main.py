import telebot
import requests
import json
from datetime import datetime
from threading import Thread
from flask import Flask
import os
import random

app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 Flame Final Proxy: Online"

TOKEN = "8494305163:AAFrXuG50xpdsYS0Jz-lFPk_tEjb3y5lpV0"
bot = telebot.TeleBot(TOKEN, threaded=False)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902} 

API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_sessions = {}

def proxy_bypass_sync(cid, data_payload):
    sd = user_sessions.get(cid)
    
    # CPM1 & CPM2 Secure Database Endpoints
    base_url = "https://cp-multiplayer-default-rtdb.firebaseio.com" if sd['v'] == "CPM1" else "https://cpm-2-7cea1-default-rtdb.firebaseio.com"
    target_url = f"{base_url}/users/{sd['localid']}.json"

    # റാഡം ഡിവൈസ് ഐഡി ഉണ്ടാക്കി സെർവറിനെ പറ്റിക്കുന്നു
    device_id = "".join(random.choices("0123456789abcdef", k=16))
    
    headers = {
        "User-Agent": f"UnityPlayer/2019.4.31f1 (UnityWorks/1.0; DeviceId:{device_id})",
        "Content-Type": "application/json",
        "X-Unity-Version": "2019.4.31f1",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive"
    }
    
    params = {"auth": sd['token']}

    try:
        # PATCH ഉപയോഗിച്ച് ഡാറ്റ ഇൻജക്ട് ചെയ്യുന്നു
        response = requests.patch(target_url, params=params, json=data_payload, headers=headers, timeout=30)
        return response
    except:
        return None

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id not in ALLOWED_USERS: return
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('CPM1', 'CPM2')
    bot.send_message(message.chat.id, "🛑 **FINAL ATTEMPT: PROXY MODE**\nസെർവർ ബ്ലോക്ക് മാറ്റാൻ ശ്രമിക്കുന്നു...", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def login_init(message):
    user_sessions[message.chat.id] = {'v': message.text}
    bot.send_message(message.chat.id, "📧 ഇമെയിൽ നൽകുക:")
    bot.register_next_step_handler(message, get_pass)

def get_pass(message):
    user_sessions[message.chat.id]['email'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 പാസ്‌വേഡ് നൽകുക:")
    bot.register_next_step_handler(message, process_login)

def process_login(message):
    cid = message.chat.id
    sd = user_sessions.get(cid)
    auth_url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS[sd['v']]}"
    res = requests.post(auth_url, json={"email": sd['email'], "password": message.text.strip(), "returnSecureToken": True}).json()
    
    if 'idToken' in res:
        sd.update({'token': res['idToken'], 'localid': res['localId']})
        m = telebot.types.InlineKeyboardMarkup()
        m.add(telebot.types.InlineKeyboardButton("🔓 PROXY UNLOCK (ALL)", callback_data="proxy_all"))
        bot.send_message(cid, "🛡️ **PROXY CONNECTED!**", reply_markup=m)
    else:
        bot.send_message(cid, "❌ ലോഗിൻ നടന്നില്ല!")

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    data = {
        "money": 50000000,
        "coins": 45000,
        "w16_engine": 1,
        "houses_unlocked": 1,
        "all_wheels_unlocked": 1,
        "all_horns": 1,
        "smoke_unlocked": 1,
        "sirens_unlocked": 1,
        "engine_damage": 0
    }
    
    resp = proxy_bypass_sync(cid, data)
    
    if resp and resp.status_code == 200:
        bot.answer_callback_query(call.id, "✅ PROXY SUCCESS!")
        bot.send_message(cid, "🎉 **അവസാനം വിജയിച്ചു!**\nസെർവറിലേക്ക് ഡാറ്റ കടത്തിവിട്ടു.\n\n**ഇനി ഇത് ചെയ്യുക:**\n1. ഫോണിലെ ഗെയിം ഡാറ്റ ക്ലിയർ ചെയ്യുക.\n2. ലോഗിൻ ചെയ്യുക.\n3. Cloud Download ചെയ്യുക.")
    else:
        bot.send_message(cid, "🛑 **പരാജയപ്പെട്ടു.**\nസെർവർ ഈ മെത്തേഡും ബ്ലോക്ക് ചെയ്തു. നിങ്ങളുടെ അക്കൗണ്ട് അല്ലെങ്കിൽ നിങ്ങളുടെ ലൊക്കേഷൻ (IP) CPM പൂർണ്ണമായും ബാൻ ചെയ്തിരിക്കുകയാണ്.")

if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling(none_stop=True)).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
