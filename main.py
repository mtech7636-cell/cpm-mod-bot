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
    return "🔥 Flame Bot: System Bypass Active"

TOKEN = "8494305163:AAFrXuG50xpdsYS0Jz-lFPk_tEjb3y5lpV0"
bot = telebot.TeleBot(TOKEN, threaded=False)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902} 

API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_sessions = {}

# --- ADVANCED BYPASS LOGIC ---
def bypass_sync(cid, data_payload):
    session = user_sessions.get(cid)
    
    # ❌ 404 Error ഒഴിവാക്കാൻ ഏറ്റവും പുതിയ എൻഡ്-പോയിന്റുകൾ
    if session['v'] == "CPM1":
        url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncData"
    else:
        # CPM2 പുതിയ സെർവർ ലിങ്ക്
        url = "https://us-central1-cpm-2-7cea1.cloudfunctions.net/SyncData_AppI_64"

    # ഗെയിം ഒറിജിനൽ ആണെന്ന് തോന്നിപ്പിക്കാൻ ആവശ്യമായ 'Official Headers'
    headers = {
        "Authorization": f"Bearer {session['token']}",
        "Content-Type": "application/json",
        "X-Unity-Version": "2021.3.15f1",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; SM-G998B Build/SP1A.210812.016)",
        "Host": "us-central1-cp-multiplayer.cloudfunctions.net" if session['v'] == "CPM1" else "us-central1-cpm-2-7cea1.cloudfunctions.net",
        "Connection": "Keep-Alive"
    }
    
    ts = int(datetime.now().timestamp() * 1000)
    data_payload.update({
        "localID": session['localid'],
        "Timestamp": ts,
        "is_modded": False # സെർവർ ചെക്കിംഗ് ഒഴിവാക്കാൻ
    })
    
    payload = {"data": json.dumps(data_payload)}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        return response
    except Exception as e:
        return f"Error: {str(e)}"

# --- START & LOGIN (അതേപടി തുടരുന്നു) ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in ALLOWED_USERS:
        bot.send_message(uid, f"❌ No Access! ID: `{uid}`")
        return
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('CPM1', 'CPM2')
    bot.send_message(message.chat.id, "🏎️ **BYPASS ACTIVE (v7.0)**\nSelect Version:", reply_markup=markup)

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
    api_url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS[session['v']]}"
    res = requests.post(api_url, json={"email": session['email'], "password": message.text.strip(), "returnSecureToken": True}).json()
    
    if 'idToken' in res:
        session.update({'token': res['idToken'], 'localid': res['localId']})
        # FULL MENU
        m = telebot.types.InlineKeyboardMarkup(row_width=2)
        m.add(
            telebot.types.InlineKeyboardButton("💵 50M CASH", callback_data="m_money"),
            telebot.types.InlineKeyboardButton("🚀 W16 ENGINE", callback_data="m_w16"),
            telebot.types.InlineKeyboardButton("🏠 ALL HOUSES", callback_data="m_houses"),
            telebot.types.InlineKeyboardButton("🛞 ALL WHEELS", callback_data="m_wheels"),
            telebot.types.InlineKeyboardButton("👑 KING RANK", callback_data="m_rank"),
            telebot.types.InlineKeyboardButton("🔓 UNLOCK EVERYTHING", callback_data="m_all")
        )
        bot.send_message(cid, "✅ **SYSTEM READY!**", reply_markup=m)
    else: bot.send_message(cid, "❌ Login Failed!")

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    data = {}
    if call.data == "m_money": data = {"money": 50000000}
    elif call.data == "m_w16": data = {"w16_engine": 1}
    elif call.data == "m_all": data = {"money": 50000000, "coins": 50000, "w16_engine": 1, "houses_unlocked": 1, "all_wheels_unlocked": 1}
    # മറ്റ് ഫീച്ചറുകൾ കൂടി ചേർക്കാം...

    resp = bypass_sync(cid, data)
    
    if isinstance(resp, str):
        bot.send_message(cid, f"❌ Network Error: {resp}")
    elif resp.status_code == 200:
        bot.answer_callback_query(call.id, "✅ SUCCESS!")
        bot.send_message(cid, "🎉 **Success!**\nഗെയിം ക്ലോസ് ചെയ്ത് **Sign Out** ചെയ്ത ശേഷം വീണ്ടും **Sign In** ചെയ്യുക.")
    else:
        bot.send_message(cid, f"❌ Failed! Error: {resp.status_code}\nസെർവർ ലിങ്ക് റിജക്ട് ചെയ്തു. സെർവർ ബിസി ആയിരിക്കാം.")

if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling(none_stop=True)).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
