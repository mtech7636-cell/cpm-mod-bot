import telebot
import requests
from telebot import types
import json
from datetime import datetime
from threading import Thread
from flask import Flask
import os
import random

app = Flask('')

@app.route('/')
def home():
    return "🔥 CPM API BOT IS RUNNING!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- MUNAR TOOL API CLASS ---
BASE_URL = "https://cpmsalebot.ru/api"

class MUNAR_TOOL:
    def __init__(self, access_key: str) -> None:
        self.auth_token = None
        self.access_key = access_key

    def _request(self, endpoint: str, extra_data: dict = None) -> dict:
        data = {"account_auth": self.auth_token} if self.auth_token else {}
        if extra_data:
            data.update(extra_data)
        params = {"key": self.access_key}
        try:
            response = requests.post(f"{BASE_URL}/{endpoint}", params=params, data=data, timeout=15)
            return response.json()
        except:
            return {"ok": False, "error": "API_ERROR"}

    def login(self, email: str, password: str) -> int:
        payload = {"account_email": email, "account_password": password}
        params = {"key": self.access_key}
        try:
            response = requests.post(f"{BASE_URL}/account_login", params=params, data=payload, timeout=15)
            res = response.json()
            if res.get("ok"):
                self.auth_token = res.get("auth")
            return res.get("error")
        except:
            return 500

# --- BOT CONFIGURATION ---
TOKEN = "8314787817:AAHpZnchNnDOaLARhaVU6eNLGbyDuyjz-n0"
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902}
user_sessions = {}

# --- START ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in ALLOWED_USERS:
        return bot.reply_to(message, "❌ Access Denied. Contact Admin.")
    
    bot.send_message(message.chat.id, "📧 CPM Email നൽകുക:")
    bot.register_next_step_handler(message, get_email)

def get_email(message):
    user_sessions[message.chat.id] = {'email': message.text.strip()}
    bot.send_message(message.chat.id, "🔑 CPM Password നൽകുക:")
    bot.register_next_step_handler(message, get_password)

def get_password(message):
    user_sessions[message.chat.id]['password'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 Access Key നൽകുക (cpmsalebot key):")
    bot.register_next_step_handler(message, final_login)

def final_login(message):
    cid = message.chat.id
    access_key = message.text.strip()
    session = user_sessions.get(cid)
    
    bot.send_message(cid, "⏳ Logging into Game Server...")
    
    # Initialize Munar Tool
    cpm = MUNAR_TOOL(access_key)
    error_code = cpm.login(session['email'], session['password'])
    
    if error_code == 0: # 0 means success
        session['cpm'] = cpm
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("💰 ADD 50M MONEY", callback_data="add_money"),
            types.InlineKeyboardButton("🪙 ADD 45K COINS", callback_data="add_coins"),
            types.InlineKeyboardButton("🔓 UNLOCK ALL CARS", callback_data="unlock_all"),
            types.InlineKeyboardButton("🏠 UNLOCK HOUSES", callback_data="unlock_house"),
            types.InlineKeyboardButton("🚫 DEL FRIENDS", callback_data="del_friends")
        )
        bot.send_message(cid, f"✅ Login Success!\nEmail: {session['email']}", reply_markup=markup)
    else:
        bot.send_message(cid, f"❌ Login Failed! Error Code: {error_code}")

# --- CALLBACKS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_actions(call):
    cid = call.message.chat.id
    session = user_sessions.get(cid)
    if not session or 'cpm' not in session:
        return bot.answer_callback_query(call.id, "Session Expired!")

    cpm = session['cpm']
    
    if call.data == "add_money":
        if cpm._request("set_money", {"amount": 50000000}).get("ok"):
            bot.send_message(cid, "✅ 50M Money Added!")
        else:
            bot.send_message(cid, "❌ Failed to add money.")

    elif call.data == "add_coins":
        if cpm._request("set_coins", {"amount": 45000}).get("ok"):
            bot.send_message(cid, "✅ 45K Coins Added!")
        else:
            bot.send_message(cid, "❌ Failed.")

    elif call.data == "unlock_all":
        cpm._request("unlock_all_cars")
        bot.send_message(cid, "✅ All Cars Unlocked!")

# --- RUN ---
if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling()
