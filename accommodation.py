from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import db
from keyboards import main_keyboard, back_keyboard
from validators import validate_input
from constants import GROUP_ID, ACCOMMODATION_THREAD_ID

# مدیریت فرآیند اسکان
async def handle_accommodation(update: Update, context: ContextTypes.DEFAULT_TYPE,section,user):
    user_message = update.message.text

    if section == 'accommodation_name':
        # اعتبارسنجی نام و نام خانوادگی
        error = validate_input("name", user_message)
        if error:
            await update.message.reply_text(error)
        else:
            context.user_data['name'] = user_message
            context.user_data['section'] = 'accommodation_student_id'
            await update.message.reply_text("لطفاً شماره دانشجویی خود را وارد کنید:", reply_markup=back_keyboard())


    elif section == 'accommodation_student_id':

        # اعتبارسنجی شماره دانشجویی

        error = validate_input("student_id", user_message)

        if error:

            await update.message.reply_text(error)

        else:

            context.user_data['student_id'] = user_message

            context.user_data['section'] = 'accommodation_national_id'

            await update.message.reply_text("لطفاً کد ملی خود را وارد کنید:", reply_markup=back_keyboard())


    elif section == 'accommodation_national_id':

        # اعتبارسنجی کد ملی

        error = validate_input("national_id", user_message)

        if error:

            await update.message.reply_text(error)

        else:

            context.user_data['national_id'] = user_message

            context.user_data['section'] = 'accommodation_room_block'

            await update.message.reply_text("لطفاً شماره اتاق و بلوک خود را وارد کنید (مثال: 1-229):",
                                            reply_markup=back_keyboard())


    elif section == 'accommodation_room_block':

        # اعتبارسنجی شماره اتاق و بلوک

        error = validate_input("room_block", user_message)

        if error:

            await update.message.reply_text(error)

        else:

            context.user_data['room_block'] = user_message

            message_id = update.message.message_id

            # ذخیره اطلاعات در دیتابیس

            db.update_user(user.id,user.username, context.user_data['name'], context.user_data['student_id'],
                           context.user_data['national_id'], context.user_data['room_block'])

            # ارسال پیام به گروه همراه با دکمه پاسخ

            reply_markup = InlineKeyboardMarkup([

                [InlineKeyboardButton("پاسخ دادن به پیام", callback_data=f'reply_{message_id}_{user.id}_accommodation')]

            ])

            await context.bot.send_message(

                chat_id=GROUP_ID,

                text=f"درخواست اسکان از {user.username}:\nنام: {context.user_data['name']}\nشماره دانشجویی: {context.user_data['student_id']}\nکد ملی: {context.user_data['national_id']}\nشماره اتاق و بلوک: {context.user_data['room_block']}",

                message_thread_id=ACCOMMODATION_THREAD_ID,

                reply_markup=reply_markup

            )

            await update.message.reply_text("✅ درخواست شما با موفقیت ثبت شد و در اسرع وقت به آن رسیدگی خواهد شد.")

            await update.message.reply_text("لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=main_keyboard)