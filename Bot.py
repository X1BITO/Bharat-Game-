import telebot
from telebot.types import InputFile

API_TOKEN = "8009527341:AAFlAPDVP0htdsBd_FQvUGoMz5KAJLEPVPw"
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🎉 Welcome to Bharat Game Bot 🇮🇳")

@bot.message_handler(commands=['deposit'])
def deposit(message):
    qr = InputFile("qr.png")
    bot.send_photo(message.chat.id, qr, caption="💳 UPI ID: dixituchiha99@fam\nMinimum deposit: ₹100")

bot.infinity_polling()
