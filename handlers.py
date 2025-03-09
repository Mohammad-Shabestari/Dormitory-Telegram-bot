from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from constants import *
from keyboards import *
from lost_and_found import handle_lost_item, handle_found_item, handle_lost_found_steps, show_registered_items
from feedback_requests import handle_feedback_or_request
from accommodation import handle_accommodation
from callback_handlers import robot_to_user_response
from notifications import send_message_to_all_users
from database import db

# مدیریت دکمه به‌روزرسانی ربات
async def update_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ ربات با موفقیت به روزرسانی شد.")
    await start(update, context)


# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if db.get_user(user.id) == None:
        db.insert_user(user.id,user.username,user.full_name, "null","null", "null")

    member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=update.effective_user.id)

    if member.status:
        await update.message.reply_text('لطفاً یکی از گزینه‌ها را انتخاب کنید:', reply_markup=main_keyboard)
    else:
        keyboard = [[KeyboardButton("بررسی عضویت")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text('برای استفاده از ربات، ابتدا باید عضویت خود در کانال خوابگاه احمدی روشن(@khabgah_Roshan) را تایید کنید:', reply_markup=reply_markup)


# مدیریت پیام‌های کاربران و ذخیره در دیتابیس
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_message = update.message.text

    # چک کردن اینکه آیا پیام در یک گروه ارسال شده و از طریق دکمه شیشه‌ای نیست
    if update.message.chat.type == 'group' or update.message.chat.type == 'supergroup':
        # اگر context.user_data مربوط به پاسخ نیست، پیام را نادیده بگیرد
        if 'reply_to_message_id' not in context.user_data:
            return

        # اگر در حال پاسخ دادن به یک پیام است
        original_user_id = context.user_data.get('reply_to_user_id')
        section_type = context.user_data.get('section_type')

        if original_user_id:
            await robot_to_user_response(update, context,section_type=section_type,original_user_id=original_user_id,user_message=user_message)
        return

    # افزودن بخش دکمه بازگشت به منوی اصلی
    elif user_message == "بازگشت به منوی اصلی":
        context.user_data.clear()
        await update.message.reply_text("به منوی اصلی بازگشتید.", reply_markup=main_keyboard)

    # بررسی پیام کاربر برای انتخاب یکی از گزینه‌های معتبر
    elif user_message == "انتقادات و پیشنهادات":
        context.user_data['section'] = 'feedback'
        await update.message.reply_text("لطفاً پیام خود را بنویسید:", reply_markup=back_keyboard())

    elif user_message == "ثبت درخواست و گزارش":
        context.user_data['section'] = 'requests'
        await update.message.reply_text("لطفاً پیام خود را بنویسید:", reply_markup=back_keyboard())

    elif user_message == "تایید درخواست اسکان و اقامت":
        context.user_data['section'] = 'accommodation_name'
        await update.message.reply_text("لطفاً نام و نام خانوادگی خود را وارد کنید:", reply_markup=back_keyboard())

    elif user_message == "گم شده و پیدا شده":
        await update.message.reply_text(
            "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("ثبت اشیا گم‌شده")],
                [KeyboardButton("ثبت اشیا پیدا‌شده")],
                [KeyboardButton("اشیا ثبت‌شده")],
                [KeyboardButton("بازگشت به منوی اصلی")]
            ], resize_keyboard=True)
        )

    elif user_message == "ثبت اشیا گم‌شده":
        await handle_lost_item(update, context)

    elif user_message == "ثبت اشیا پیدا‌شده":
        await handle_found_item(update, context)

    elif user_message == "اشیا ثبت‌شده":
        await show_registered_items(update, context)

    else:

        section = context.user_data.get('section')

        if section:
            if section in ['feedback', 'requests']:
                await handle_feedback_or_request(update, context,section=section)

            elif section.startswith("accommodation"):
                await handle_accommodation(update, context,section=section,user=user)

        else:
            # اگر کاربر پیام بی‌ربط وارد کند
            try:
                await handle_lost_found_steps(update, context)
            except:
                if user.id in ADMINS and user_message.startswith(SPECIAL_KEYWORD):

                    # حذف واژه خاص از ابتدای پیام
                    message_to_send = user_message[len(SPECIAL_KEYWORD):].strip()

                    # ارسال پیام به همه کاربران عضو ربات
                    await send_message_to_all_users(context, message_to_send)
                    await update.message.reply_text("✅ پیام با موفقیت به همه کاربران ارسال شد.")
                else:
                    await update.message.reply_text("لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=main_keyboard)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    context.user_data['image'] = photo.file_id
    context.user_data['step'] = 'photo'
    await handle_lost_found_steps(update, context)