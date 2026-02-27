import telebot
import requests
from telebot import types
import json
import random
import datetime
from threading import Thread
from flask import Flask
import os

app = Flask('')

@app.route('/')
def home():
    return "🔥 Flame Bot + Black Market Key System is Online!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURATION ---
TOKEN = "8314787817:AAHpZnchNnDOaLARhaVU6eNLGbyDuyjz-n0"
bot = telebot.TeleBot(TOKEN, threaded=True)

ADMIN_ID = 7212602902
ALLOWED_USERS = {7212602902}
KEY_FILE = "keys.txt"

# വിലയും ദിവസവും (RM എന്നത് പകരമായി നിങ്ങൾക്ക് രൂപയോ പോയിന്റോ ആക്കാം)
PLAN = {"20": 7, "50": 30, "100": 0} # 0 എന്നാൽ Lifetime

# --- START MENU ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # യൂസർ മെനു
    btn1 = types.InlineKeyboardButton("🛒 BUY KEY", callback_data="buy_key")
    btn2 = types.InlineKeyboardButton("🔐 CHECK KEY", callback_data="check_key")
    btn3 = types.InlineKeyboardButton("🔥 OPEN TOOLS", callback_data="open_tools")
    markup.add(btn1, btn2, btn3)
    
    # അഡ്മിൻ മെനു (അഡ്മിന് മാത്രം കാണുന്നത്)
    if uid == ADMIN_ID:
        btn4 = types.InlineKeyboardButton("🛠 GEN KEY", callback_data="admin_gen")
        btn5 = types.InlineKeyboardButton("📁 ALL KEYS", callback_data="admin_keys")
        markup.add(btn4, btn5)

    bot.send_message(message.chat.id, 
        f"🏁 **BLACK MARKET CPM BOT**\n\nഹലോ {message.from_user.first_name},\nസിസ്റ്റം ഇപ്പോൾ ആക്ടീവ് ആണ്. താഴെ ഉള്ള ഓപ്ഷനുകൾ ഉപയോഗിക്കുക.", 
        reply_markup=markup, parse_mode='Markdown')

# --- KEY GENERATOR (ADMIN ONLY) ---
@bot.message_handler(commands=['genkey'])
def genkey_command(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "❌ ആക്സസ് നിഷേധിച്ചു.")

    try:
        args = message.text.split()
        amount = args[1] # ഉദാഹരണത്തിന്: /genkey 20
        days = PLAN.get(amount)
        
        if days is None:
            return bot.reply_to(message, "❌ തെറ്റായ വില. /buy നോക്കുക.")

        key = "BM-" + ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=12))
        expiry = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d") if days > 0 else "LIFETIME"

        with open(KEY_FILE, "a") as f:
            f.write(f"{key}|{expiry}\n")

        bot.reply_to(message, f"✅ **Key Generated:** `{key}`\n📅 **Expiry:** {expiry}", parse_mode='Markdown')
    except:
        bot.reply_to(message, "ഉപയോഗിക്കേണ്ട രീതി: `/genkey 20` (അല്ലെങ്കിൽ 50, 100)")

# --- CHECK KEY ---
@bot.message_handler(commands=['check'])
def check_key(message):
    try:
        key_input = message.text.split()[1].upper()
        found = False
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "r") as f:
                for line in f:
                    k, exp = line.strip().split("|")
                    if key_input == k:
                        bot.reply_to(message, f"✅ Key Valid!\n📅 Expiry: {exp}")
                        found = True
                        break
        if not found: bot.reply_to(message, "❌ Invalid Key!")
    except:
        bot.reply_to(message, "ഉപയോഗം: `/check BM-XXXXXX`")

# --- CALLBACKS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == "buy_key":
        bot.send_message(call.message.chat.id, "🛒 **Buy Key:** @XIIXMMI ബന്ധപ്പെടുക.")
    elif call.data == "admin_gen":
        bot.send_message(call.message.chat.id, "കീ ഉണ്ടാക്കാൻ `/genkey 20` എന്ന് ടൈപ്പ് ചെയ്യുക.")
    elif call.data == "admin_keys":
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "r") as f:
                data = f.read()
            bot.send_message(call.message.chat.id, f"📁 **All Keys:**\n\n{data}")
        else:
            bot.send_message(call.message.chat.id, "No keys found.")

# --- RUN SERVER ---
if __name__ == "__main__":
    if not os.path.exists(KEY_FILE): open(KEY_FILE, "w").close()
    Thread(target=run_flask).start()
    bot.infinity_polling()
