
import telebot
import json
import os
from datetime import datetime

# === Bot Configuration ===
API_TOKEN = "8009527341:AAE5TwInlG1EBHLO86bwiAOUYK54RZ1iAz8"
bot = telebot.TeleBot(API_TOKEN)
ADMIN_IDS = ["6201560180"]
QR_UPI_ID = "dixituchiha99@fam"
QR_IMAGE = "qr.png"

# === Ensure Required Files Exist ===
default_files = {
    "data.json": {},
    "pending_txns.json": {},
    "coupons.json": {}
}

for file, default in default_files.items():
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump(default, f)

# Dummy QR if not exists
if not os.path.exists(QR_IMAGE):
    with open(QR_IMAGE, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")

# === Load Data ===
def load(path):
    with open(path) as f: return json.load(f)

def save(path, data):
    with open(path, "w") as f: json.dump(data, f, indent=2)

users = load("data.json")
txns = load("pending_txns.json")
coupons = load("coupons.json")

# === User Helper ===
def get_user(uid):
    uid = str(uid)
    if uid not in users:
        users[uid] = {"wallet": 0, "ref": "", "joined": str(datetime.now()), "daily": ""}
    return users[uid]

# === Bot Commands ===
@bot.message_handler(commands=["start"])
def cmd_start(msg):
    uid = str(msg.from_user.id)
    ref = msg.text.split()[1] if len(msg.text.split()) > 1 else ""
    new = uid not in users
    user = get_user(uid)
    if new and ref in users and ref != uid:
        users[ref]["wallet"] += 5
        user["ref"] = ref
    save("data.json", users)
    bot.reply_to(msg, "👋 Welcome to Bharat Game Bot 🇮🇳\nUse /wallet, /deposit, /withdraw, /daily, /coupon")

@bot.message_handler(commands=["wallet"])
def cmd_wallet(msg):
    uid = str(msg.from_user.id)
    bal = get_user(uid)["wallet"]
    bot.reply_to(msg, f"💰 Wallet: ₹{bal}")

@bot.message_handler(commands=["deposit"])
def cmd_deposit(msg):
    with open(QR_IMAGE, "rb") as qr:
        bot.send_photo(msg.chat.id, qr, caption=f"💳 Send to UPI: {QR_UPI_ID}\nMin: ₹100\nThen use /submit TXNID")

@bot.message_handler(commands=["submit"])
def cmd_submit(msg):
    uid = str(msg.from_user.id)
    parts = msg.text.split()
    if len(parts) != 2: return bot.reply_to(msg, "Use: /submit TXNID123")
    txns[uid] = {"txn": parts[1]}
    save("pending_txns.json", txns)
    for aid in ADMIN_IDS:
        bot.send_message(aid, f"🆕 TXN from {uid}: {parts[1]}")
    bot.reply_to(msg, "✅ Submitted! Waiting admin approval.")

@bot.message_handler(commands=["approve"])
def cmd_approve(msg):
    if str(msg.from_user.id) not in ADMIN_IDS: return
    parts = msg.text.split()
    if len(parts) != 3: return bot.reply_to(msg, "Use: /approve USERID AMOUNT")
    uid, amount = parts[1], int(parts[2])
    get_user(uid)["wallet"] += amount
    txns.pop(uid, None)
    save("data.json", users)
    save("pending_txns.json", txns)
    bot.send_message(uid, f"✅ ₹{amount} added to your wallet.")

@bot.message_handler(commands=["withdraw"])
def cmd_withdraw(msg):
    uid = str(msg.from_user.id)
    user = get_user(uid)
    if user["wallet"] < 500:
        return bot.reply_to(msg, "❌ Min withdraw ₹500")
    amount = user["wallet"]
    admin_amount = int(amount * 0.20)
    bot.reply_to(msg, f"💸 Withdraw sent: ₹{amount - admin_amount} (20% fee)")
    for aid in ADMIN_IDS:
        bot.send_message(aid, f"💸 Withdraw: {uid} wants ₹{amount}")
    user["wallet"] = 0
    save("data.json", users)

@bot.message_handler(commands=["daily"])
def cmd_daily(msg):
    uid = str(msg.from_user.id)
    user = get_user(uid)
    now = datetime.now().strftime("%Y-%m-%d")
    if user["daily"] == now:
        return bot.reply_to(msg, "❌ Already claimed today.")
    user["wallet"] += 10
    user["daily"] = now
    save("data.json", users)
    bot.reply_to(msg, "🎁 Daily bonus ₹10 added!")

@bot.message_handler(commands=["coupon"])
def cmd_coupon(msg):
    uid = str(msg.from_user.id)
    parts = msg.text.split()
    if len(parts) != 2:
        return bot.reply_to(msg, "Use: /coupon CODE")
    code = parts[1]
    if code in coupons and not coupons[code].get("used", False):
        amt = coupons[code]["amount"]
        get_user(uid)["wallet"] += amt
        coupons[code]["used"] = True
        bot.reply_to(msg, f"✅ ₹{amt} added!")
    else:
        bot.reply_to(msg, "❌ Invalid or used code.")
    save("data.json", users)
    save("coupons.json", coupons)

# === Run the bot ===
print("✅ Bharat Game Bot running...")
bot.infinity_polling()
