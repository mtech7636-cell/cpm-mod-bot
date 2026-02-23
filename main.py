import telebot
from telebot import types
import os
from threading import Thread
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>🤖 CPM ELITE STABLE v6.0: ACTIVE</h1>"

# നിങ്ങളുടെ പുതിയ ടോക്കൺ
TOKEN = "8494305163:AAH6XQAfy91mrmi4e4TO5JtFBE7gTDL0hjY"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 7212602902 

# ബോട്ട് ഉപയോഗിക്കുന്നവരുടെ ലിസ്റ്റ് സൂക്ഷിക്കാൻ
users = set()

# --- 1. START MENU ---
@bot.message_handler(commands=['start'])
def start(message):
    users.add(message.chat.id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🛒 CAR MARKET", callback_data="market")
    btn2 = types.InlineKeyboardButton("🎨 LIVERY STORE", callback_data="livery")
    btn3 = types.InlineKeyboardButton("📊 MY PROFILE", callback_data="profile")
    btn4 = types.InlineKeyboardButton("📢 UPDATES", callback_data="updates")
    markup.add(btn1, btn2, btn3, btn4)
    
    welcome = (f"🏎️ **CPM ELITE HELPER v6.0**\n\n"
               f"ഹലോ {message.from_user.first_name}!\n"
               f"CPM ഗെയിമിലെ ഏറ്റവും പുതിയ ഡിസൈനുകളും മാർക്കറ്റ് വിവരങ്ങളും ഇവിടെ ലഭിക്കും.")
    bot.send_message(message.chat.id, welcome, reply_markup=markup, parse_mode="Markdown")

# --- 2. ADMIN BROADCAST (ഫീച്ചർ 4) ---
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id == ADMIN_ID:
        msg_text = message.text.replace('/broadcast ', '')
        if msg_text == "/broadcast" or msg_text == "":
            bot.send_message(ADMIN_ID, "❌ ഉപയോഗിക്കേണ്ട രീതി: `/broadcast നിങ്ങളുടെ മെസ്സേജ്`")
            return
        
        success = 0
        for user_id in users:
            try:
                bot.send_message(user_id, f"📢 **OFFICIAL ANNOUNCEMENT**\n\n{msg_text}")
                success += 1
            except: continue
        bot.send_message(ADMIN_ID, f"✅ {success} പ്ലെയേഴ്സിന് മെസ്സേജ് അയച്ചു.")

# --- CALLBACK RESPONSES ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    uid = call.message.chat.id
    
    # 🛒 CAR MARKET (ഫീച്ചർ 3)
    if call.data == "market":
        market_text = ("🛒 **CPM MARKETPLACE**\n\n"
                       "നിങ്ങൾക്ക് വണ്ടി വിൽക്കാനുണ്ടോ? എങ്കിൽ വണ്ടിയുടെ ഫോട്ടോയും വിലയും അഡ്മിന് അയക്കുക.\n\n"
                       "അഡ്മിൻ: @YourUsername")
        bot.send_message(uid, market_text)

    # 🎨 LIVERY STORE
    elif call.data == "livery":
        livery_text = ("🎨 **EXCLUSIVE LIVERY CODES**\n\n"
                       "• Police Mustang: `PM-001` \n"
                       "• Tokyo Drift: `TD-77` \n"
                       "• Monster Truck: `MT-55` \n\n"
                       "ഈ കോഡുകൾ ഗെയിമിൽ ഉപയോഗിക്കാം!")
        bot.send_message(uid, livery_text)

    # 📊 PROFILE
    elif call.data == "profile":
        bot.send_message(uid, f"📊 **PLAYER INFO**\n\n👤 Name: {call.from_user.first_name}\n🆔 ID: `{uid}`\n🚀 Rank: Member")

    # 📢 UPDATES
    elif call.data == "updates":
        bot.send_message(uid, "📢 **NEWS & UPDATES**\n\nനിലവിൽ ബോട്ട് വളരെ സ്മൂത്ത് ആയി വർക്ക് ചെയ്യുന്നു. പുതിയ ഡിസൈനുകൾ ഉടൻ തന്നെ സ്റ്റോറിൽ ആഡ് ചെയ്യുന്നതാണ്!")

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
