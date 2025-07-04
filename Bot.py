
import telebot
from telebot.types import InputFile
import json
import os
from datetime import datetime

# Telegram Bot Token
API_TOKEN = "8009527341:AAFlAPDVP0htdsBd_FQvUGoMz5KAJLEPVPw"
bot = telebot.TeleBot(API_TOKEN)

# /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome to Bharat Game Bot 🇮🇳\nUse /deposit to see QR\nUse /wallet to check your balance.")

# /deposit command - shows UPI QR and info
@bot.message_handler(commands=['deposit'])
def deposit(message):
    try:
        qr = InputFile("qr.png")
        bot.send_photo(message.chat.id, qr, caption="📥 UPI ID: 7037391707@fam\n💸 Minimum Deposit: ₹100\n🧾 Send /submit after payment to send TXN ID.")
    except:
        bot.reply_to(message, "❌ QR code not found. Please upload 'qr.png'.")

# /wallet command - check balance
@bot.message_handler(commands=['wallet'])
def wallet(message):
    user_id = str(message.from_user.id)
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            users = json.load(f)
    else:
        users = {}
    if user_id not in users:
        users[user_id] = {"wallet": 0, "daily_claimed": ""}
        with open("users.json", "w") as f:
            json.dump(users, f, indent=4)
    balance = users[user_id]["wallet"]
    bot.reply_to(message, f"💰 Your current wallet balance is ₹{balance}")

# /submit command - UPI Transaction ID submission
@bot.message_handler(commands=['submit'])
def submit_txn(message):
    msg = bot.reply_to(message, "📩 Please enter your UPI Transaction ID:")
    bot.register_next_step_handler(msg, save_txn)

def save_txn(message):
    user_id = str(message.from_user.id)
    txn_id = message.text.strip()
    if os.path.exists("pending_txns.json"):
        with open("pending_txns.json", "r") as f:
            txns = json.load(f)
    else:
        txns = {}
    txns[user_id] = txn_id
    with open("pending_txns.json", "w") as f:
        json.dump(txns, f, indent=4)
    bot.reply_to(message, f"✅ Transaction ID received:\n🧾 `{txn_id}`\nPlease wait for admin approval.", parse_mode='Markdown')

# /daily command - ₹10 daily reward (24hr cooldown)
@bot.message_handler(commands=['daily'])
def daily_reward(message):
    user_id = str(message.from_user.id)
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            users = json.load(f)
    else:
        users = {}
    if user_id not in users:
        users[user_id] = {"wallet": 0, "daily_claimed": ""}
    last_claimed = users[user_id].get("daily_claimed", "")
    if last_claimed == today:
        bot.reply_to(message, "🕒 You already claimed your daily reward today.")
    else:
        users[user_id]["wallet"] += 10
        users[user_id]["daily_claimed"] = today
        with open("users.json", "w") as f:
            json.dump(users, f, indent=4)
        bot.reply_to(message, "🎁 You've received ₹10 daily reward! Check /wallet to see your updated balance.")

# Start the bot
bot.infinity_polling()
