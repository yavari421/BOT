import os
import telebot
import sqlite3
# TOKEN = "8296249064:AAHU5ycJcXzgId3nFNsA5Q6vjjyKfWwP4l8"



import sqlite3
import telebot
import os

# دیتابیس
conn = sqlite3.connect("contacts.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS contacts(
    telegram_id TEXT,
    name TEXT,
    phone TEXT
)
""")
conn.commit()

# # /start
# @bot.message_handler(commands=['start'])
# def start(message):
#     bot.send_message(message.chat.id, "سلام! لطفا شماره تماس خود را ارسال کنید.")

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
    
# دریافت شماره
@bot.message_handler(content_types=['contact'])
def contact(message):
    telegram_id = message.from_user.id
    name = message.from_user.first_name
    phone = message.contact.phone_number

    cursor.execute("INSERT INTO contacts VALUES (?,?,?)", (telegram_id, name, phone))
    conn.commit()
    bot.send_message(message.chat.id, "شماره شما ثبت شد.\nلینک: https://example.com")

# نمایش شماره‌ها (chunk برای پیام طولانی)
@bot.message_handler(commands=['showcontacts'])
def show_contacts(message):
    cursor.execute("SELECT * FROM contacts")
    rows = cursor.fetchall()
    if rows:
        data = "\n".join([f"{r[0]}, {r[1]}, {r[2]}" for r in rows])
        for chunk in [data[i:i+4000] for i in range(0, len(data), 4000)]:
            bot.send_message(message.chat.id, chunk)
    else:
        bot.send_message(message.chat.id, "شماره‌ای موجود نیست.")

# دانلود CSV
@bot.message_handler(commands=['download'])
def download_file(message):
    import csv
    cursor.execute("SELECT * FROM contacts")
    rows = cursor.fetchall()
    if rows:
        with open("contacts.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["telegram_id", "name", "phone"])
            writer.writerows(rows)
        with open("contacts.csv", "rb") as f:
            bot.send_document(message.chat.id, f)
    else:
        bot.send_message(message.chat.id, "فایلی برای ارسال موجود نیست.")

bot.polling()
