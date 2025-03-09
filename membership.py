from telegram import Update
from telegram.ext import ContextTypes
from keyboards import main_keyboard
from constants import CHANNEL_USERNAME

# بررسی عضویت کاربر در کانال
async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user.id)
        if member.status not in ['member', 'administrator', 'creator']:
            await update.message.reply_text('شما هنوز در کانال عضو نشده‌اید. لطفاً ابتدا در کانال زیر عضو شوید:\n' + CHANNEL_USERNAME)
        else:
            await update.message.reply_text('عضویت شما تایید شد. حالا می‌توانید از امکانات ربات استفاده کنید.')
            await update.message.reply_text("لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=main_keyboard)
            context.user_data['is_member'] = True
    except Exception:
        await update.message.reply_text('خطایی رخ داده است. لطفاً دوباره امتحان کنید.')
