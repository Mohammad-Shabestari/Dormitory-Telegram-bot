from telegram.ext import ContextTypes
from database import db  # فرض می‌کنیم که اطلاعات کاربران در دیتابیس ذخیره می‌شود

async def send_message_to_all_users(context: ContextTypes.DEFAULT_TYPE, message: str):
    # دریافت لیست کاربران عضو از دیتابیس
    users = db.get_all_users()  # تابعی فرضی که لیست کاربران عضو را بازمی‌گرداند
    print(users)
    for user in users:
        try:
            await context.bot.send_message(chat_id=user['telegram_id'], text=message)
        except Exception as e:
            print(f"خطا در ارسال پیام به کاربر {user['telegram_id']}: {e}")
