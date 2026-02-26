import telebot
import requests
from telebot import types
import json
from datetime import datetime
from threading import Thread
from flask import Flask
import os

app = Flask('')

@app.route('/')
def home():
    return "🔥 CPM API BOT IS FULLY ACTIVE!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- FULL MUNAR TOOL CLASS ---
BASE_URL = "https://cpmsalebot.ru/api"

class MUNAR_TOOL:
    def __init__(self, access_key: str) -> None:
        self.auth_token = None
        self.access_key = access_key

    def _request(self, endpoint: str, extra_data: dict = None) -> dict:
        data = {"account_auth": self.auth_token} if self.auth_token else {}
        if extra_data: data.update(extra_data)
        params = {"key": self.access_key}
        try:
            response = requests.post(f"{BASE_URL}/{endpoint}", params=params, data=data, timeout=20)
            return response.json()
        except: return {"ok": False}

    def login(self, email: str, password: str) -> int:
        payload = {"account_email": email, "account_password": password}
        params = {"key": self.access_key}
        try:
            res = requests.post(f"{BASE_URL}/account_login", params=params, data=payload, timeout=20).json()
            if res.get("ok"): self.auth_token = res.get("auth")
            return res.get("error")
        except: return 500

# --- BOT CONFIG ---
TOKEN = "8314787817:AAHpZnchNnDOaLARhaVU6eNLGbyDuyjz-n0"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 7212602902
user_sessions = {}

# --- LOGIN HANDLERS ---
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID: return
    bot.send_message(message.chat.id, "📧 Email നൽകുക:")
    bot.register_next_step_handler(message, lambda m: get_field(m, 'email', "🔑 Password നൽകുക:", get_field))

def get_field(message, field, next_msg, next_func):
    user_sessions[message.chat.id] = user_sessions.get(message.chat.id, {})
    user_sessions[message.chat.id][field] = message.text.strip()
    if field == 'email':
        bot.send_message(message.chat.id, "🔑 Password നൽകുക:")
        bot.register_next_step_handler(message, lambda m: get_field(m, 'password', "🔑 Access Key നൽകുക:", final_step))
    elif field == 'password':
        bot.send_message(message.chat.id, "🔑 Access Key നൽകുക:")
        bot.register_next_step_handler(message, final_step)

def final_step(message):
    cid = message.chat.id
    key = message.text.strip()
    session = user_sessions.get(cid)
    cpm = MUNAR_TOOL(key)
    bot.send_message(cid, "⏳ ലോഗിൻ ചെയ്യുന്നു...")
    if cpm.login(session['email'], session['password']) == 0:
        session['cpm'] = cpm
        show_menu(cid)
    else: bot.send_message(cid, "❌ ലോഗിൻ പരാജയപ്പെട്ടു!")

def show_menu(cid):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [
        ("💰 50M Money", "set_money"), ("🪙 45K Coins", "set_coins"),
        ("👑 Rank", "set_rank"), ("🚗 Unlock Cars", "unlock_cars"),
        ("🚨 Siren", "unlock_siren"), ("🔧 W16 Engine", "unlock_w16"),
        ("🏠 Houses", "unlock_houses"), ("💨 Smoke", "unlock_smoke"),
        ("🔢 Plates", "set_plates"), ("🏁 Race Wins", "set_wins"),
        ("🚫 Del Friends", "del_friends"), ("💥 No Damage", "no_damage")
    ]
    for text, data in btns: markup.insert(types.InlineKeyboardButton(text, callback_data=data))
    bot.send_message(cid, "🔥 **CPM FULL MENU**", reply_markup=markup)

# --- CALLBACKS FOR ALL API FEATURES ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    cid = call.message.chat.id
    cpm = user_sessions.get(cid, {}).get('cpm')
    if not cpm: return

    actions = {
        "set_money": ("set_money", {"amount": 50000000}),
        "set_coins": ("set_coins", {"amount": 45000}),
        "unlock_cars": ("unlock_all_cars", {}),
        "unlock_siren": ("unlock_all_cars_siren", {}),
        "unlock_w16": ("unlock_w16", {}),
        "unlock_houses": ("unlock_houses", {}),
        "unlock_smoke": ("unlock_smoke", {}),
        "set_plates": ("set_plates", {}),
        "del_friends": ("delete_friends", {}),
        "no_damage": ("disable_damage", {}),
        "set_wins": ("set_race_wins", {"amount": 5000})
    }

    if call.data in actions:
        endpoint, data = actions[call.data]
        res = cpm._request(endpoint, data)
        msg = "✅ വിജയിച്ചു!" if res.get("ok") else "❌ പരാജയപ്പെട്ടു!"
        bot.answer_callback_query(call.id, msg)
        bot.send_message(cid, f"**{call.data.replace('_',' ').upper()}**: {msg}")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling()
