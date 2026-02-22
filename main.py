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
    return "🔥 Flame Mega Bot is Online & Fully Fixed!"

TOKEN = "8494305163:AAFrXuG50xpdsYS0Jz-lFPk_tEjb3y5lpV0"
bot = telebot.TeleBot(TOKEN, threaded=False)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902} 

API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_sessions = {}

# --- FORCE SYNC LOGIC (The Secret Sauce) ---
def force_sync(cid, data_payload):
    session = user_sessions.get(cid)
    # ഗെയിം ഒറിജിനൽ ആയി അയക്കുന്ന രീതിയിലുള്ള Headers
    headers = {
        "Authorization": f"Bearer {session['token']}",
        "Content-Type": "application/json",
        "X-Unity-Version": "2019.4.31f1",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; Pixel 6 Build/SD1A.210817.036)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    
    ts = int(datetime.now().timestamp() * 1000)
    # സെർവർ റിജക്ട് ചെയ്യാതിരിക്കാൻ localID കൃത്യമായി അയക്കുന്നു
    data_payload.update({
        "localID": session['localid'],
        "Timestamp": ts,
        "is_online": True
    })
    
    payload = {"data": json.dumps(data_payload)}
    
    # CPM1 & CPM2 Endpoints
    url = "https://us-central1-cp-multiplayer.cloudfunctions.net/SyncData"
    if session['v'] == "CPM2":
        url = "https://us-central1-cpm-2-7cea1.cloudfunctions.net/SyncData_AppI"
        
    return requests.post(url, headers=headers, json=payload)

# --- START & LOGIN ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in ALLOWED_USERS:
        bot.send_message(uid, f"❌ No Access! ID: `{uid}`")
        return
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('CPM1', 'CPM2')
    bot.send_message(message.chat.id, "🏎️ **FLAME MEGA TOOL v4**\nVersion സെലക്ട് ചെയ്യുക:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def login_init(message):
    user_sessions[message.chat.id] = {'v': message.text}
    bot.send_message(message.chat.id, "📧 Email നൽകുക:", reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_pass)

def get_pass(message):
    user_sessions[message.chat.id]['email'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 Password നൽകുക:")
    bot.register_next_step_handler(message, process_login)

def process_login(message):
    cid = message.chat.id
    session = user_sessions.get(cid)
    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS[session['v']]}"
    res = requests.post(url, json={"email": session['email'], "password": message.text.strip(), "returnSecureToken": True}).json()
    
    if 'idToken' in res:
        session.update({'token': res['idToken'], 'localid': res['localId']})
        # MAIN MENU
        m = telebot.types.InlineKeyboardMarkup(row_width=1)
        m.add(
            telebot.types.InlineKeyboardButton("💰 50M CASH + 50K COINS", callback_data="do_money"),
            telebot.types.InlineKeyboardButton("🚀 UNLOCK W16 + MODS", callback_data="do_mods"),
            telebot.types.InlineKeyboardButton("🏠 UNLOCK ALL HOUSES", callback_data="do_houses"),
            telebot.types.InlineKeyboardButton("🛞 PAID WHEELS", callback_data="do_wheels"),
            telebot.types.InlineKeyboardButton("👑 KING RANK", callback_data="do_rank"),
            telebot.types.InlineKeyboardButton("🔓 UNLOCK EVERYTHING", callback_data="do_all")
        )
        bot.send_message(cid, "✅ **Login Success!**\nഎന്ത് വേണം?", reply_markup=m)
    else: bot.send_message(cid, "❌ Login Failed!")

# --- ACTION CALLBACKS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    data = {}
    
    if call.data == "do_money": data = {"money": 50000000, "coins": 50000}
    elif call.data == "do_mods": data = {"w16_engine": 1, "smoke_unlocked": 1, "all_horns": 1, "engine_damage": 0}
    elif call.data == "do_houses": data = {"houses_unlocked": 1}
    elif call.data == "do_wheels": data = {"all_wheels_unlocked": 1}
    elif call.data == "do_rank": data = {"race_win": 9999, "is_king": True}
    elif call.data == "do_all": data = {"money": 50000000, "coins": 50000, "w16_engine": 1, "houses_unlocked": 1, "all_wheels_unlocked": 1, "all_horns": 1, "smoke_unlocked": 1, "engine_damage": 0}
    
    resp = force_sync(cid, data)
    if resp.status_code == 200:
        bot.answer_callback_query(call.id, "✅ SENT TO SERVER!")
        bot.send_message(cid, "🎉 **Success!**\n\n⚠️ **ഇതുകൂടി ചെയ്തില്ലെങ്കിൽ ഗെയിമിൽ വരില്ല:**\n1. ഫോണിലെ ഗെയിം **Clear Data** ചെയ്യുക.\n2. ഗെയിം തുറന്ന് **Account**-ൽ പോയി ലോഗിൻ ചെയ്യുക.\n3. അപ്പോൾ ബോട്ട് വഴി സെറ്റ് ചെയ്ത പുതിയ വാല്യൂസ് ഫോണിലേക്ക് ലോഡ് ആകും.")
    else:
        bot.send_message(cid, f"❌ Failed: {resp.status_code}")

if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling(none_stop=True)).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
