
import telebot
from telebot.types import InputFile
import json
import os
from datetime import datetime

API_TOKEN = "8009527341:AAE5TwInlG1EBHLO86bwiAOUYK54RZ1iAz8"
bot = telebot.TeleBot(API_TOKEN)

DATA_FILE = "data.json"
TXN_FILE = "pending_txns.json"
COUPON_FILE = "coupons.json"

ADMIN_IDS = ["6201560180"]  # Add your Telegram user ID here

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def ensure_user(user):
    data = load_json(DATA_FILE)
    uid = str(user.id)
    if uid not in data:
        data[uid] = {
            "username": user.username or "",
            "wallet": 0,
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "daily_claimed": "",
            "referrer": "",
            "history": [],
        }
        save_json(DATA_FILE, data)

@bot.message_handler(commands=['start'])
def start(message):
    ensure_user(message.from_user)
    bot.reply_to(message, "🎮 Welcome to Bharat Game Bot! 🇮🇳\nUse /wallet, /deposit, /daily, /coupon, /referral, /withdraw")

@bot.message_handler(commands=['wallet'])
def wallet(message):
    uid = str(message.from_user.id)
    data = load_json(DATA_FILE)
    bal = data.get(uid, {}).get("wallet", 0)
    bot.reply_to(message, f"💰 Your wallet balance: ₹{bal}")

@bot.message_handler(commands=['deposit'])
def deposit(message):
    qr = InputFile("qr.png")
    bot.send_photo(message.chat.id, qr, caption="💳 UPI ID: dixituchiha99@fam\nMinimum Deposit: ₹100\nUse /submit after payment.")

@bot.message_handler(commands=['submit'])
def submit(message):
    msg = bot.reply_to(message, "📩 Enter your UPI Transaction ID:")
    bot.register_next_step_handler(msg, save_txn)

def save_txn(message):
    txns = load_json(TXN_FILE)
    uid = str(message.from_user.id)
    txns[uid] = message.text.strip()
    save_json(TXN_FILE, txns)
    bot.reply_to(message, "🧾 Transaction ID submitted. Wait for admin approval.")

@bot.message_handler(commands=['daily'])
def daily(message):
    uid = str(message.from_user.id)
    data = load_json(DATA_FILE)
    user = data.get(uid, {})
    today = datetime.now().strftime("%Y-%m-%d")
    if user.get("daily_claimed") == today:
        bot.reply_to(message, "🕒 Already claimed today.")
    else:
        user["wallet"] += 10
        user["daily_claimed"] = today
        data[uid] = user
        save_json(DATA_FILE, data)
        bot.reply_to(message, "🎁 ₹10 daily reward added to wallet!")

@bot.message_handler(commands=['coupon'])
def coupon(message):
    msg = bot.reply_to(message, "🔤 Enter your coupon code:")
    bot.register_next_step_handler(msg, apply_coupon)

def apply_coupon(message):
    uid = str(message.from_user.id)
    code = message.text.strip().lower()
    coupons = load_json(COUPON_FILE)
    data = load_json(DATA_FILE)
    if code in coupons and not coupons[code].get("used", False):
        amt = coupons[code]["amount"]
        data[uid]["wallet"] += amt
        data[uid]["history"].append(f"Coupon {code} +₹{amt}")
        coupons[code]["used"] = True
        save_json(COUPON_FILE, coupons)
        save_json(DATA_FILE, data)
        bot.reply_to(message, f"✅ Coupon applied! ₹{amt} added.")
    else:
        bot.reply_to(message, "❌ Invalid or already used coupon.")

@bot.message_handler(commands=['referral'])
def referral(message):
    uid = str(message.from_user.id)
    bot.reply_to(message, f"🔗 Your referral link:\nhttps://t.me/BharatGameBot?start={uid}")

@bot.message_handler(commands=['withdraw'])
def withdraw(message):
    uid = str(message.from_user.id)
    data = load_json(DATA_FILE)
    bal = data.get(uid, {}).get("wallet", 0)
    if bal < 50000:
        bot.reply_to(message, "❌ Minimum withdrawal is ₹50,000.")
    else:
        admin_uid = ADMIN_IDS[0]
        bot.reply_to(message, "✅ Withdrawal request sent to admin.")
        bot.send_message(admin_uid, f"🧾 Withdrawal Request:\nUser: {uid}\nAmount: ₹{bal}\n20% Commission deducted.")
        data[uid]["wallet"] = 0
        save_json(DATA_FILE, data)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return bot.reply_to(message, "⛔ Access denied.")
    txns = load_json(TXN_FILE)
    if not txns:
        return bot.reply_to(message, "📭 No pending TXNs.")
    for uid, txn in txns.items():
        bot.send_message(message.chat.id, f"🧾 TXN from {uid}: {txn}")

bot.infinity_polling()
