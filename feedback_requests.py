from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import db
from keyboards import main_keyboard, back_keyboard
from constants import GROUP_ID, FEEDBACK_THREAD_ID, REQUESTS_THREAD_ID

# مدیریت پیام‌های بخش انتقادات و پیشنهادات و گزارشات
async def handle_feedback_or_request(update: Update, context: ContextTypes.DEFAULT_TYPE,section):

    user = update.effective_user
    user_message = update.message.text

    message_id = update.message.message_id

    # ذخیره پیام در دیتابیس
    db.insert_message(user.id, message_id, section, user_message)

    # ارسال پیام به گروه همراه با دکمه "پاسخ دادن به پیام"
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("پاسخ دادن به پیام", callback_data=f'reply_{message_id}_{user.id}_{section}')]
    ])

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"🔻انتقاد/پیشنهاد🔻 از 👤 @{user.username} 👤 \n\n{user_message}" if section == 'feedback' else f"🔻درخواست/گزارش🔻 از @{user.username} \n\n{user_message}",
        message_thread_id=FEEDBACK_THREAD_ID if section == 'feedback' else REQUESTS_THREAD_ID,
        reply_markup=reply_markup
    )

    await update.message.reply_text(
        f"✅ نظر شما با موفقیت ثبت شد.از ثبت بازخوردتان متشکریم\n «« تیم سرپرستی خوابگاه احمدی روشن »»"
        if section == 'feedback'
        else
        f"✅ درخواست/گزارش شما با موفقیت ثبت شده و در اسرع وقت به آن رسیدگی خواهد شد.\n «« تیم سرپرستی خوابگاه احمدی روشن »»",
        reply_markup=main_keyboard
    )
