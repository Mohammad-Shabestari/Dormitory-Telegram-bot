from telegram import Update
from telegram.ext import ContextTypes
from database import db

# مدیریت پاسخ به پیام در گروه و ارسال به کاربر اصلی
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # استخراج message_id از callback_data
    callback_data = query.data.split('_')
    if len(callback_data) < 4:
        await query.message.reply_text("خطا در پردازش درخواست. لطفاً دوباره تلاش کنید.")
        return

    message_id = int(callback_data[1])
    user_id = int(callback_data[2])
    section_type = callback_data[3]

    # دریافت اطلاعات پیام اصلی
    original_message_record = db.get_message_by_message_id(message_id)

    if original_message_record or section_type == 'accommodation':
        try:
            original_user_id = original_message_record[1]
        except:
            original_user_id = user_id

        # ذخیره message_id برای ارسال پاسخ
        context.user_data['reply_to_message_id'] = message_id
        context.user_data['reply_to_user_id'] = original_user_id
        context.user_data['section_type'] = section_type

        # ارسال پیام به گروه برای گرفتن ورودی پاسخ
        await query.message.reply_text("پاسخ خود را بنویسید:")
    else:
        await query.message.reply_text("پیام اصلی پیدا نشد.")





async def robot_to_user_response(update: Update, context: ContextTypes.DEFAULT_TYPE,section_type,original_user_id,user_message):
    if section_type == 'accommodation':
        # ارسال پیام بدون ریپلای به کاربر
        await context.bot.send_message(
            chat_id=original_user_id,
            text=f"نتیجه درخواست اقامت شما:\n\n{user_message}"
        )
        await update.message.reply_text("پاسخ شما ارسال شد.")
    else:
        # ارسال پیام به کاربر و ریپلای روی پیام اصلی
        await context.bot.send_message(
            chat_id=original_user_id,
            text=f'پاسخ جدید برای پیام شما:\n\n{user_message}',
            reply_to_message_id=context.user_data['reply_to_message_id']
        )
        await update.message.reply_text("پاسخ شما ارسال شد.")

    # پاک کردن اطلاعات مربوط به پاسخ
    del context.user_data['reply_to_message_id']
    del context.user_data['reply_to_user_id']
    del context.user_data['section_type']