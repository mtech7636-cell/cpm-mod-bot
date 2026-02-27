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
    return "🔥 Flame Bot is Fixed & Ready!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

TOKEN = "8314787817:AAHpZnchNnDOaLARhaVU6eNLGbyDuyjz-n0"
bot = telebot.TeleBot(TOKEN, threaded=True)

ADMIN_ID = 7212602902
KEY_FILE = "keys.txt"
user_sessions = {}

# --- START ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 ENTER KEY", callback_data="enter_key"))
    bot.send_message(message.chat.id, "🏁 **FLAME MASTER BOT**\n\nതുടങ്ങാൻ നിങ്ങളുടെ Key നൽകുക.", reply_markup=markup, parse_mode='Markdown')

# --- HANDLING KEY TEXT ---
@bot.message_handler(func=lambda m: m.text.startswith("BM-") or len(m.text) > 10)
def verify_key_text(message):
    key_input = message.text.strip().upper()
    found = False
    
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            for line in f:
                if key_input in line:
                    found = True
                    break
    
    if found:
        user_sessions[message.chat.id] = {'authenticated': True}
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add('CPM1', 'CPM2')
        bot.send_message(message.chat.id, "✅ **Key Verified!**\nഇനി ഗെയിം വേർഷൻ തിരഞ്ഞെടുക്കുക:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ തെറ്റായ കീ! പുതിയ കീ വാങ്ങാൻ അഡ്മിനെ ബന്ധപ്പെടുക.")

# --- VERSION SELECTION & LOGIN ---
@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def select_version(message):
    if message.chat.id in user_sessions and user_sessions[message.chat.id].get('authenticated'):
        user_sessions[message.chat.id]['v'] = message.text
        bot.send_message(message.chat.id, f"📧 {message.text} സെലക്ട് ചെയ്തു.\nഇനി നിങ്ങളുടെ **Email** നൽകുക:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_email)
    else:
        bot.send_message(message.chat.id, "⚠️ ദയവായി ആദ്യം കീ നൽകുക.")

def get_email(message):
    user_sessions[message.chat.id]['email'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 ഇനി **Password** നൽകുക:")
    bot.register_next_step_handler(message, process_login)

def process_login(message):
    # പഴയ ലോഗിൻ ടാസ്ക് (Firebase Logic) ഇവിടെ വരും...
    bot.send_message(message.chat.id, "⏳ ലോഗിൻ ചെയ്യുന്നു...")
    # (മുൻപ് നൽകിയ ലോഗിൻ കോഡ് ഇതിന്റെ താഴെ പേസ്റ്റ് ചെയ്യാം)

# --- SERVER RUN ---
if __name__ == "__main__":
    if not os.path.exists(KEY_FILE): open(KEY_FILE, "w").close()
    Thread(target=run_flask).start()
    bot.infinity_polling()
