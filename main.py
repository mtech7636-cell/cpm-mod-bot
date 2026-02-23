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
    return "🔥 Flame Final Rescue Mode"

TOKEN = "8494305163:AAFrXuG50xpdsYS0Jz-lFPk_tEjb3y5lpV0"
bot = telebot.TeleBot(TOKEN, threaded=False)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902} 

API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_sessions = {}

def secure_inject(cid, data_payload):
    session = user_sessions.get(cid)
    
    # CPM1 & CPM2 Secure Database Endpoints
    if session['v'] == "CPM1":
        base_url = "https://cp-multiplayer-default-rtdb.firebaseio.com"
    else:
        base_url = "https://cpm-2-7cea1-default-rtdb.firebaseio.com"

    # ഡയറക്ട് യൂസർ റൂട്ടിലേക്ക് ഡാറ്റ വിടുന്നു
    target_url = f"{base_url}/users/{session['localid']}.json?auth={session['token']}"
    
    headers = {
        "User-Agent": "UnityPlayer/2021.3.15f1",
        "Content-Type": "application/json"
    }

    try:
        # പുഷ് ചെയ്യാൻ PATCH തന്നെ വേണം, പക്ഷേ ടൈംഔട്ട് കൂട്ടി നൽകുന്നു
        res = requests.patch(target_url, json=data_payload, headers=headers, timeout=40)
        return res
    except:
        return None

# --- ലോഗിൻ ഫ്ലോ ---
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id not in ALLOWED_USERS: return
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('CPM1', 'CPM2')
    bot.send_message(message.chat.id, "🛡️ **RESCUE PANEL v10.0**\nവിശ്വാസം നിലനിർത്താൻ അവസാന ശ്രമം:", reply_markup=markup)

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
    session = user_sessions.get(cid)
    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS[session['v']]}"
    res = requests.post(url, json={"email": session['email'], "password": message.text.strip(), "returnSecureToken": True}).json()
    
    if 'idToken' in res:
        session.update({'token': res['idToken'], 'localid': res['localId']})
        m = telebot.types.InlineKeyboardMarkup()
        m.add(telebot.types.InlineKeyboardButton("🚀 FORCE UNLOCK ALL", callback_data="force_all"))
        bot.send_message(cid, "✅ **CONNECTED!**\nഇതൊന്ന് ട്രൈ ചെയ്യൂ:", reply_markup=m)
    else:
        bot.send_message(cid, "❌ ലോഗിൻ പരാജയപ്പെട്ടു!")

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    # എല്ലാ ഫീച്ചറുകളും ഉൾപ്പെടുത്തിയ പായ്ക്ക്
    data = {
        "money": 50000000,
        "coins": 50000,
        "w16_engine": 1,
        "all_horns": 1,
        "smoke_unlocked": 1,
        "houses_unlocked": 1,
        "all_wheels_unlocked": 1,
        "sirens_unlocked": 1,
        "engine_damage": 0
    }
    
    resp = secure_inject(cid, data)
    
    if resp and resp.status_code == 200:
        bot.answer_callback_query(call.id, "✅ INJECTED!")
        bot.send_message(cid, "🎉 **അവസാനം സക്സസ് ആയി!**\n\nഗെയിം റീസ്റ്റാർട്ട് ചെയ്ത് നോക്കൂ. വന്നിട്ടുണ്ടാകും. വന്നിട്ടില്ലെങ്കിൽ ഗെയിം **Clear Data** ചെയ്യുക. ലോഗിൻ ചെയ്യുമ്പോൾ എല്ലാം അവിടെയുണ്ടാകും.")
    else:
        bot.send_message(cid, "❌ സെർവർ റെസ്പോണ്ട് ചെയ്യുന്നില്ല. ഒരു 5 മിനിറ്റ് കഴിഞ്ഞ് നോക്കൂ.")

if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling(none_stop=True)).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
