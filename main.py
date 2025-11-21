import os
import telebot

# TOKEN = "8296249064:AAHU5ycJcXzgId3nFNsA5Q6vjjyKfWwP4l8"


# توکن را از Environment Variable می‌خوانیم
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "سلام! لطفا شماره تماس خود را ارسال کنید.")

@bot.message_handler(content_types=['contact'])
def contact(message):
    with open("contacts.csv", "a", encoding="utf-8") as f:
        f.write(f"{message.from_user.id},{message.from_user.first_name},{message.contact.phone_number}\n")
    bot.send_message(message.chat.id, "شماره شما ثبت شد.\nلینک: https://example.com")

@bot.message_handler(commands=['showcontacts'])
def show_contacts(message):
    try:
        with open("contacts.csv", "r", encoding="utf-8") as f:
            data = f.read()
        if data:
            bot.send_message(message.chat.id, f"شماره‌ها:\n{data}")
        else:
            bot.send_message(message.chat.id, "فایل خالی است.")
    except FileNotFoundError:
        bot.send_message(message.chat.id, "فایل موجود نیست.")


bot.polling()
