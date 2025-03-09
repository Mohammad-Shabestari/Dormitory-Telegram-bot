import asyncio
from schedule_delete import cleanup_task
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from handlers import start, handle_message, update_bot,handle_photo
from membership import check_membership
from callback_handlers import handle_callback_query
from constants import TELEGRAM_BOT_API_TOKEN
from lost_and_found import handle_lost_found_callback, handle_returned


if __name__ == '__main__':
    # اجرای ربات تلگرام
    app = ApplicationBuilder().token(TELEGRAM_BOT_API_TOKEN).build()

    # هندلرها
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.Regex('^بررسی عضویت$'), check_membership))
    app.add_handler(MessageHandler(filters.Regex('^به‌روزرسانی ربات$'), update_bot))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # هندلر برای پاسخ به دکمه‌های شیشه‌ای
    app.add_handler(CallbackQueryHandler(handle_lost_found_callback, pattern='^(approve_ad|reject_ad)_[0-9]+$'))
    app.add_handler(CallbackQueryHandler(handle_returned, pattern='^return_[0-9]+$'))
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    # اجرای ربات و زمان‌بندی به صورت هم‌زمان
    loop = asyncio.get_event_loop()
    loop.create_task(cleanup_task())
    print("Bot is running...")
    app.run_polling()
