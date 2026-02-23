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
    return "🔥 Flame Bot: Ready to Go"

TOKEN = "8494305163:AAFrXuG50xpdsYS0Jz-lFPk_tEjb3y5lpV0"
bot = telebot.TeleBot(TOKEN, threaded=False)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902} 

API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_sessions = {}

def direct_push(cid, key, value):
    sd = user_sessions.get(cid)
    base = "https://cp-multiplayer-default-rtdb.firebaseio.com" if sd['v'] == "CPM1" else "https://cpm-2-7cea1-default-rtdb.firebaseio.com"
    
    # ഓരോ വാല്യൂവും ഓരോന്നായി പുഷ് ചെയ്യുന്നു
    url = f"{base}/users/{sd['localid']}/{key}.json?auth={sd['token']}"
    
    try:
        # PUT ഉപയോഗിച്ച് കൃത്യം ആ സ്ഥലത്തേക്ക് ഡാറ്റ എത്തിക്കുന്നു
        res = requests.put(url, json=value, timeout=15)
        return res.status_code == 200
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id not in ALLOWED_USERS: return
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('CPM1', 'CPM2')
    bot.send_message(message.chat.id, "🏎️ **CPM DIRECT TOOL**\nVPN ആവശ്യമില്ല, നേരിട്ട് നോക്കാം:", reply_markup=markup)

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
    auth_url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS[sd['v']]}"
    res = requests.post(auth_url, json={"email": sd['email'], "password": message.text.strip(), "returnSecureToken": True}).json()
    
    if 'idToken' in res:
        sd.update({'token': res['idToken'], 'localid': res['localId']})
        m = telebot.types.InlineKeyboardMarkup()
        m.add(telebot.types.InlineKeyboardButton("💰 ADD 50M & 50K", callback_data="add_money"))
        bot.send_message(cid, "✅ **Logged In!**", reply_markup=m)
    else:
        bot.send_message(cid, "❌ Login Error!")

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    bot.answer_callback_query(call.id, "Processing...")
    
    # പണവും കോയിനും ഓരോന്നായി മാറ്റുന്നു
    s1 = direct_push(cid, "money", 50000000)
    s2 = direct_push(cid, "coins", 50000)
    s3 = direct_push(cid, "w16_engine", 1)
    
    if s1 or s2:
        bot.send_message(cid, "✅ **Success!**\nസെർവറിൽ മാറ്റം വരുത്തി. ഇനി ഗെയിം **Clear Data** ചെയ്ത് ലോഗിൻ ചെയ്തു നോക്കൂ.")
    else:
        bot.send_message(cid, "❌ സെർവർ ഇപ്പോഴും ബ്ലോക്ക് ചെയ്യുന്നു. ഇമെയിൽ ലോഗിൻ ഔട്ട് ചെയ്തിട്ടുണ്ടാകാം.")

if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling(none_stop=True)).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
