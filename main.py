import os
import telebot
import sqlite3
# TOKEN = "8296249064:AAHU5ycJcXzgId3nFNsA5Q6vjjyKfWwP4l8"


# توکن را از Environment Variable می‌خوانیم
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, """👋 سلام و خوش اومدی به ربات استعدادیابی برنامه‌نویسی نوجوانان!

اینجا می‌تونی در کمتر از ۳ دقیقه بفهمی آیا ذهن و استعدادت برای یادگیری برنامه‌نویسی ساخته شده یا نه.

تست ما خیلی ساده‌ست: فقط چند سؤال کوتاه و تصویری که بهت کمک می‌کنه مسیر یادگیری خودت رو بهتر بشناسی.

در ابتدای ورود، شماره تماس‌ت رو می‌گیریم تا نتیجه تست رو مستقیم برات ارسال کنیم و اگر خواستی، مشاوره رایگان هم داشته باشی.

🎯 هدف ما اینه که قبل از شروع دوره، مطمئن بشی مسیرت درسته و با انگیزه وارد یادگیری بشی.
آماده‌ای شروع کنیم؟ 🚀! لطفا شماره تماس خود را ارسال کنید.""")

conn = sqlite3.connect("contacts.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS contacts(
    telegram_id TEXT,
    name TEXT,
    phone TEXT
)
""")
conn.commit()

@bot.message_handler(content_types=['contact'])
def contact(message):
    telegram_id = message.from_user.id
    name = message.from_user.first_name
    phone = message.contact.phone_number

    cursor.execute("INSERT INTO contacts VALUES (?,?,?)", (telegram_id, name, phone))
    conn.commit()
    bot.send_message(message.chat.id, "شماره شما ثبت شد.\nلینک: https://example.com")
    
# @bot.message_handler(content_types=['contact'])
# def contact(message):
#     with open("contacts.csv", "a", encoding="utf-8") as f:
#         f.write(f"{message.from_user.id},{message.from_user.first_name},{message.contact.phone_number}\n")
#     bot.send_message(message.chat.id, "شماره شما ثبت شد.\nلینک: https://example.com")

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
