from telegram import KeyboardButton, ReplyKeyboardMarkup

main_keyboard = ReplyKeyboardMarkup(
    [
        ["انتقادات و پیشنهادات", "ثبت درخواست و گزارش"],
        ["تایید درخواست اسکان و اقامت", "گم شده و پیدا شده"],
        ["به‌روزرسانی ربات"]

    ],
    resize_keyboard=True
)

# تعریف کیبورد بازگشت به منوی اصلی
def back_keyboard():
    keyboard = [[KeyboardButton("بازگشت به منوی اصلی")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)