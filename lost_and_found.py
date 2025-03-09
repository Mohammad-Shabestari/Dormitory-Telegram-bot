from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update,ReplyKeyboardMarkup,KeyboardButton
from telegram.ext import ContextTypes
from constants import LOST_AND_FOUND_THREAD_ID, CHANNEL_ID, GROUP_ID
from database import db
from keyboards import main_keyboard

# Display questions for registering a lost item
async def handle_lost_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لطفاً عنوان شی گم‌شده را وارد کنید:")
    context.user_data['lost_and_found'] = 'lost'
    context.user_data['step'] = 'title'

# Display questions for registering a found item
async def handle_found_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لطفاً عنوان شی پیدا‌شده را وارد کنید:")
    context.user_data['lost_and_found'] = 'found'
    context.user_data['step'] = 'title'

# Handle registration steps for lost and found items
# اصلاح شده: مدیریت مراحل ثبت اشیا گم شده و پیدا شده
async def handle_lost_found_steps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # استفاده از کلید اختصاصی برای مدیریت مراحل بخش گم‌شده و پیدا شده
    step = context.user_data.get('step', None)

    if step is None:
        raise
        return

    if step == 'title':
        context.user_data['title'] = update.message.text
        await update.message.reply_text("لطفاً توضیحات مربوط به شی را وارد کنید:")
        context.user_data['step'] = 'description'

    elif step == 'description':
        context.user_data['description'] = update.message.text

        if context.user_data['lost_and_found'] == 'lost':

            await update.message.reply_text("در صورت داشتن عکس از شی گم‌شده، آن را ارسال کنید یا گزینه 'عکسی ندارم' را بزنید.",reply_markup=ReplyKeyboardMarkup([
                    [KeyboardButton("عکسی ندارم")],
                ], resize_keyboard=True))
            context.user_data['step'] = 'photo'
        else:
            await update.message.reply_text(
                "لطفاً آیدی خود یا شخص مربوطه برای ارتباط را وارد کنید:",
            )
            context.user_data['step'] = 'contact'

    elif step == 'photo':

        if update.message.text:
                # بررسی اگر کاربر "عکسی ندارم" ارسال کرده است
            if update.message.text.strip() == "عکسی ندارم":
                context.user_data['image'] = None

                # اگر نه عکسی ارسال شده و نه "عکسی ندارم" وارد شده
            else:
                await update.message.reply_text("لطفاً یا عکسی ارسال کنید یا دقیقاً عبارت 'عکسی ندارم' را وارد کنید.",reply_markup=ReplyKeyboardMarkup([
                        [KeyboardButton("عکسی ندارم")],
                    ], resize_keyboard=True))
                return  # توقف عملیات در صورت ورود نادرست

        await update.message.reply_text("لطفاً آیدی خود یا شخص مربوطه برای ارتباط را وارد کنید:")
        context.user_data['step'] = 'contact'

    elif step == 'contact':
        context.user_data['contact'] = update.message.text
        await send_lost_found_ad(update, context)

    else:
        await update.message.reply_text("لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=main_keyboard)



# Send the ad to the group for approval
async def send_lost_found_ad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ad_type = "گم‌شده" if context.user_data['lost_and_found'] == 'lost' else "پیدا‌شده"
    ad_text = f"#{ad_type}\n\nعنوان: {context.user_data['title']}\nتوضیحات: {context.user_data['description']}\nآیدی: {context.user_data['contact']}"
    image = context.user_data.get('image')
    try:
        # ثبت آگهی در دیتابیس
        ad_id = db.insert_lost_found_item(
            user_id=update.effective_user.id,
            item_type=ad_type,
            title=context.user_data['title'],
            description=context.user_data['description'],
            contact=context.user_data['contact'],
            photo = context.user_data['image']
        )

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ تایید آگهی", callback_data=f'approve_ad_{ad_id}')],
            [InlineKeyboardButton("⛔️ رد آگهی", callback_data=f'reject_ad_{ad_id}')]
        ])

        if image:
            await context.bot.send_photo(
                chat_id=GROUP_ID,
                photo=image,
                caption=ad_text,
                reply_markup=reply_markup,
                message_thread_id=LOST_AND_FOUND_THREAD_ID
            )
        else:
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=ad_text,
                reply_markup=reply_markup,
                message_thread_id=LOST_AND_FOUND_THREAD_ID
            )

        await update.message.reply_text("✅ آگهی شما برای تایید ارسال شد.",reply_markup=main_keyboard)


    except Exception as e:
        await update.message.reply_text("⚠️ خطایی در ارسال آگهی به گروه رخ داد. لطفاً بعداً دوباره تلاش کنید.")
        print(f"Error sending message to group: {e}")


# مدیریت تایید یا رد آگهی
async def handle_lost_found_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split('_')
    action = data[0]
    ad_id = data[2]

    item = db.get_lost_found_item(ad_id)
    if item:
        user_id = item[1]

        if action == 'approve':
            if context.user_data.get('image'):
                channel_message = await context.bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=context.user_data.get('image'),
                    caption=query.message.caption
                )
            else:
                channel_message = await context.bot.send_message(chat_id=CHANNEL_ID, text=query.message.text)

            channel_message_id = channel_message.message_id

            # ذخیره آیدی پیام کانال در دیتابیس
            db.update_channel_message_id(ad_id, channel_message_id)

            await query.message.delete()
            await context.bot.send_message(chat_id=user_id, text="✅ آگهی شما تایید شد و در کانال ارسال گردید.")

        elif action == 'reject':
            await query.message.delete()
            await context.bot.send_message(chat_id=user_id, text="⛔️ آگهی شما رد شد.")




# Handle marking item as returned or collected
async def handle_returned(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    ad_id = query.data.split('_')[1]  # دریافت ID آگهی

    item = db.get_lost_found_item(ad_id)  # فرض کنید تابعی برای دریافت آگهی بر اساس ID دارید

    if item:
        channel_message_id = item[8] # فرض بر این که در دیتابیس ستون channel_message_id دارید

        ad_text = f"#{item[2]}\n\nعنوان: {item[3]}\nتوضیحات: {item[4]}\n\n وضعیت: {'پیدا شده' if item[2] == 'گم‌شده' else 'تحویل داده شد'}"

        # ویرایش پیام در کانال
        try:
            await context.bot.edit_message_text(
                chat_id=CHANNEL_ID,
                message_id=channel_message_id,
                text=ad_text
            )
        except:
            await context.bot.edit_message_caption(
                chat_id=CHANNEL_ID,
                message_id=channel_message_id,
                caption=ad_text
            )
        await query.answer("✅ وضعیت آگهی با موفقیت به‌روزرسانی شد.")



# نمایش اشیا ثبت شده برای به‌روزرسانی وضعیت
async def show_registered_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    items = db.get_user_lost_found_items(user_id, status='pending')

    if items:
        for item in items:
            ad_type = "گم‌شده" if item[2] == 'گم‌شده' else "پیدا‌شده"
            ad_text = f"#{ad_type}\n\nعنوان: {item[3]}\nتوضیحات: {item[4]}\nآیدی: {item[5]}"

            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("تحویل گرفتم/تحویل دادم", callback_data=f'return_{item[0]}')]
            ])

            await update.message.reply_text(ad_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text("هیچ آیتمی ثبت نشده است.")


