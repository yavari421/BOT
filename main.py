import sqlite3
import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


# ---------------- DATABASE INIT ---------------- #
def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    
    # جدول کاربران + شماره تماس + id تلگرام
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            name TEXT,
            phone TEXT
        )
    """)
    
    # جدول پاسخ‌ها
    c.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            chat_id INTEGER,
            q1 TEXT,
            q2 TEXT,
            q3 TEXT,
            q4 TEXT,
            q5 TEXT
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

# ---------------- QUESTIONS ---------------- #
QUESTIONS = [
    "سؤال ۱: اگر بخوای یه لیست از نمرات رو مرتب کنی، کدوم روش بهتره؟\n1. از بزرگ به کوچک\n2. از کوچک به بزرگ\n3. بر اساس میانگین\n4. نمی‌دانم",
    "سؤال ۲: وقتی یه بازی می‌سازی، اول باید چی رو مشخص کنی؟\n1. رنگ‌ها و گرافیک  \n2. قوانین و هدف بازی \n3. اسم بازی  \n4. تعداد بازیکن‌ها",
    "سؤال ۳: اگر یه ربات داشته باشی که باید از یه مسیر پیچیده عبور کنه، چی براش مهم‌تره؟\n1. سرعت حرکت  \n2. نقشه مسیر  \n3. رنگ ربات  \n4. تعداد چرخ‌ها",
    "سؤال ۴: کدوم جمله بیشتر بهت حس خوبی می‌ده؟\n1. وقتی یه مسئله سخت رو حل می‌کنم   \n2.  وقتی یه چیز جدید می‌سازم  \n3. وقتی با دوستام بازی می‌کنم  \n4. وقتی چیزی رو سریع یاد می‌گیرم",
    "سؤال ۵: اگه یه کد بنویسی و کار نکنه، چی کار می‌کنی؟\n1.  سریع بی‌خیال می‌شی  \n2. دنبال ایرادش می‌گردی  \n3. از کسی کمک می‌گیری  \n4. دوباره از اول می‌نویسی"
]

# ---------------- USER MEMORY ---------------- #
WAITING_FOR_PHONE = {}
USER_STATE = {}
USER_ANSWERS = {}

# ---------------- HELPERS ---------------- #
def is_valid_choice(x):
    return x in ["1", "2", "3", "4"]

# ---------------- HANDLERS ---------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    name = update.message.from_user.first_name

    WAITING_FOR_PHONE[chat_id] = True  # منتظر شماره تماس
    
    # دکمه ارسال شماره
    kb = [[KeyboardButton("📱 ارسال شماره تماس", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)

    await update.message.reply_text(
        f"""سلام {name} 👋\n\nخوش اومدی به ربات استعدادیابی برنامه‌نویسی نوجوانان!

اینجا می‌تونی در کمتر از ۳ دقیقه بفهمی آیا ذهن و استعدادت برای یادگیری برنامه‌نویسی ساخته شده یا نه.

تست ما خیلی ساده‌ست: فقط چند سؤال کوتاه و تصویری که بهت کمک می‌کنه مسیر یادگیری خودت رو بهتر بشناسی.

در ابتدای ورود، شماره تماس‌ت رو می‌گیریم تا نتیجه تست رو مستقیم برات ارسال کنیم و اگر خواستی، مشاوره رایگان هم داشته باشی.

🎯 هدف ما اینه که قبل از شروع دوره، مطمئن بشی مسیرت درسته و با انگیزه وارد یادگیری بشی.

📞 لطفاً شماره تماس خود را ارسال کنید (یا از دکمه ارسال شماره استفاده کنید)""",
        reply_markup=reply_markup
    )


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    
    if chat_id not in WAITING_FOR_PHONE:
        return

    # گرفتن شماره کانتکت
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()

    # اعتبارسنجی دستی
    if not phone.startswith(("09", "+989")):
        await update.message.reply_text("❌ لطفاً یک شماره معتبر ارسال کنید.\nمثال: 09121234567")
        return

    # ذخیره در دیتابیس
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute("""
        INSERT OR REPLACE INTO users (chat_id, name, phone)
        VALUES (?, ?, ?)
    """, (chat_id, update.message.from_user.first_name, phone))

    conn.commit()
    conn.close()

    # شروع آزمون
    del WAITING_FOR_PHONE[chat_id]
    USER_STATE[chat_id] = 0
    USER_ANSWERS[chat_id] = {}

    await update.message.reply_text("شماره با موفقیت ثبت شد ✔\n\nبریم سراغ سوالات…")
    await update.message.reply_text(QUESTIONS[0])


async def answers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text.strip()

    # اگر شماره نگرفته بود
    if chat_id in WAITING_FOR_PHONE:
        await update.message.reply_text("❗ لطفاً ابتدا شماره تماس را ارسال کنید.")
        return

    # اگر آزمون فعال نیست
    if chat_id not in USER_STATE:
        await update.message.reply_text("برای شروع تست، دستور /start را بزنید.")
        return

    # اعتبارسنجی جواب
    if not is_valid_choice(text):
        await update.message.reply_text("❌ فقط عدد 1 تا 4 را وارد کنید.")
        return

    # ذخیره جواب
    question_index = USER_STATE[chat_id]
    USER_ANSWERS[chat_id][question_index] = text

    USER_STATE[chat_id] += 1

    # اگر آزمون تمام شد
    if USER_STATE[chat_id] == len(QUESTIONS):

        conn = sqlite3.connect("data.db")
        c = conn.cursor()

        c.execute("""
            INSERT INTO answers (chat_id, q1, q2, q3, q4, q5)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            chat_id,
            USER_ANSWERS[chat_id][0],
            USER_ANSWERS[chat_id][1],
            USER_ANSWERS[chat_id][2],
            USER_ANSWERS[chat_id][3],
            USER_ANSWERS[chat_id][4]
        ))

        conn.commit()
        conn.close()

        # پاک کردن وضعیت
        del USER_STATE[chat_id]
        del USER_ANSWERS[chat_id]

        await update.message.reply_text("🎉 پاسخ‌های شما با موفقیت ثبت شد!\nبه‌زودی نتیجه برای شما ارسال می‌شود 🙌")
        return

    # ارسال سؤال بعدی
    await update.message.reply_text(QUESTIONS[USER_STATE[chat_id]])


async def show_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()

    c.execute("SELECT * FROM answers")
    answers = c.fetchall()
    conn.close()

    msg = "📋 لیست کاربران:\n\n"
    for u in users:
        msg += f"ID: {u[0]} | نام: {u[1]} | تلفن: {u[2]}\n"

    msg += "\n\n📝 پاسخ‌ها:\n\n"
    for a in answers:
        msg += f"{a[0]} → {a[1]}, {a[2]}, {a[3]}, {a[4]}, {a[5]}\n"

    await update.message.reply_text(msg)


# ---------------- RUN ---------------- #
TOKEN = os.environ.get("BOT_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("show", show_all))

# شماره‌گیری
app.add_handler(MessageHandler(filters.CONTACT, get_phone))
app.add_handler(MessageHandler(filters.Regex("^(09|\\+989)"), get_phone))

# جواب‌های تست
app.add_handler(MessageHandler(filters.TEXT, answers_handler))

app.run_polling()
