import telebot

TOKEN = "8296249064:AAHU5ycJcXzgId3nFNsA5Q6vjjyKfWwP4l8"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "سلام! لطفا شماره تماس خود را ارسال کنید.")

@bot.message_handler(content_types=['contact'])
def contact(message):
    with open("contacts.csv", "a", encoding="utf-8") as f:
        f.write(f"{message.from_user.id},{message.from_user.first_name},{message.contact.phone_number}\n")
    bot.send_message(message.chat.id, "شماره شما ثبت شد.\nلینک: https://example.com")

bot.polling()
