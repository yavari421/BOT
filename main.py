import sqlite3
import telebot
import os
import re  # برای چک شماره معتبر

# -------------------------------
# دیتابیس
# -------------------------------
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

# -------------------------------
# توکن (Environment Variable)
# -------------------------------
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# -------------------------------
# /start
# -------------------------------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, """👋 سلام و خوش اومدی به ربات استعدادیابی برنامه‌نویسی نوجوانان!

اینجا می‌تونی در کمتر از ۳ دقیقه بفهمی آیا ذهن و استعدادت برای یادگیری برنامه‌نویسی ساخته شده یا نه.

تست ما خیلی ساده‌ست: فقط چند سؤال کوتاه و تصویری که بهت کمک می‌کنه مسیر یادگیری خودت رو بهتر بشناسی.

در ابتدای ورود، شماره تماس‌ت رو می‌گیریم تا نتیجه تست رو مستقیم برات ارسال کنیم و اگر خواستی، مشاوره رایگان هم داشته باشی.

🎯 هدف ما اینه که قبل از شروع دوره، مطمئن بشی مسیرت درسته و با انگیزه وارد یادگیری بشی.

📞 لطفاً شماره تماس خود را ارسال کنید (یا از دکمه ارسال شماره استفاده کنید).""")


# -------------------------------
# دریافت شماره از دکمه Contact
# -------------------------------
@bot.message_handler(content_types=['contact'])
def get_contact(message):
    telegram_id = message.from_user.id
    name = message.from_user.first_name
    phone = message.contact.phone_number

    cursor.execute("INSERT INTO contacts VALUES (?,?,?)", (telegram_id, name, phone))
    conn.commit()

    bot.send_message(message.chat.id, """شماره شما ثبت شد.  
لینک تست شما آماده است:  
https://forms.gle/eNzwQAQeopo73pnz7""")


# -------------------------------
# دریافت شماره در قالب متن + چک اعتبار
# -------------------------------
@bot.message_handler(content_types=['text'])
def get_text_number(message):
    phone = message.text.strip()

    # شماره معتبر؟ (فقط اعداد – 9 تا 15 رقم – با یا بدون +98)
    if not re.match(r'^\+?\d{9,15}$', phone):
        bot.send_message(
            message.chat.id,
            "❌ شماره معتبر نیست.\nمثال صحیح: 09123456789 یا +989123456789"
        )
        return

    telegram_id = message.from_user.id
    name = message.from_user.first_name

    cursor.execute("INSERT INTO contacts VALUES (?,?,?)", (telegram_id, name, phone))
    conn.commit()

    bot.send_message(message.chat.id, """شماره شما ثبت شد.  
لینک تست شما آماده است:  
https://forms.gle/eNzwQAQeopo73pnz7""")


# -------------------------------
# فرمان نمایش شماره‌ها
# -------------------------------
@bot.message_handler(commands=['showcontacts'])
def show_contacts(message):
    cursor.execute("SELECT * FROM contacts")
    rows = cursor.fetchall()
    if rows:
        data = "\n".join([f"{r[0]}, {r[1]}, {r[2]}" for r in rows])
        for chunk in [data[i:i+4000] for i in range(0, len(data), 4000)]:
            bot.send_message(message.chat.id, chunk)
    else:
        bot.send_message(message.chat.id, "هیچ شماره‌ای ذخیره نشده است.")


# -------------------------------
# دانلود CSV
# -------------------------------
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
        bot.send_message(message.chat.id, "فایلی برای دانلود موجود نیست.")


# -------------------------------
# شروع Polling
# -------------------------------
bot.polling()
