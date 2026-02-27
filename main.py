import telebot
import requests
from telebot import types
import json
import random
import datetime
from threading import Thread
from flask import Flask
import os

# --- FLASK DASHBOARD ---
app = Flask('')

@app.route('/')
def home():
    return "<h1>🔥 BOT IS ALIVE & RESPONDING!</h1>"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- BOT CONFIGURATION ---
TOKEN = "8314787817:AAHpZnchNnDOaLARhaVU6eNLGbyDuyjz-n0"
bot = telebot.TeleBot(TOKEN, threaded=True)

ADMIN_ID = 7212602902
KEY_FILE = "keys.txt"
PLAN = {"20": 7, "50": 30, "100": 0}

# --- FUNCTIONS ---
def generate_key(days):
    key = "BM-" + ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=12))
    expiry = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d") if days > 0 else "LIFETIME"
    with open(KEY_FILE, "a") as f:
        f.write(f"{key}|{expiry}\n")
    return key, expiry

# --- COMMANDS ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🛒 BUY KEY", callback_data="buy")
    btn2 = types.InlineKeyboardButton("🔐 CHECK KEY", callback_data="check_status")
    btn3 = types.InlineKeyboardButton("🚀 TOOLS", callback_data="open_tools")
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(message.chat.id, "🏁 **BLACK MARKET CPM**\nസിസ്റ്റം ഇപ്പോൾ പ്രവർത്തിക്കുന്നുണ്ട്. നിങ്ങൾ എന്തിനാണ് കാത്തിരിക്കുന്നത്?", reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['genkey'])
def gen(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        amount = message.text.split()[1]
        days = PLAN.get(amount)
        if days is not None:
            k, e = generate_key(days)
            bot.reply_to(message, f"✅ **KEY:** `{k}`\n📅 **EXP:** {e}", parse_mode='Markdown')
        else:
            bot.reply_to(message, "❌ Invalid price! Use 20, 50 or 100")
    except:
        bot.reply_to(message, "Format: `/genkey 20`", parse_mode='Markdown')

# --- CALLBACKS ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "buy":
        bot.send_message(call.message.chat.id, "🛒 ബന്ധപ്പെടുക: @XIIXMMI")
    elif call.data == "check_status":
        bot.send_message(call.message.chat.id, "നിങ്ങളുടെ Key പരിശോധിക്കാൻ `/check BM-XXXX` എന്ന് അയക്കുക.")
    elif call.data == "open_tools":
        bot.send_message(call.message.chat.id, "🛠 **TOOLS MENU**\n\nഈ സെക്ഷൻ ഉപയോഗിക്കാൻ നിങ്ങൾ ലോഗിൻ ചെയ്യേണ്ടതുണ്ട്. (ലോഗിൻ ഫംഗ്ഷൻ ആക്റ്റീവ് ആണ്)")

# --- START SERVER ---
if __name__ == "__main__":
    if not os.path.exists(KEY_FILE):
        open(KEY_FILE, "w").close()
    
    print("Bot is starting...")
    Thread(target=run_flask).start()
    bot.infinity_polling()
