import os
import asyncio
import logging
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# تنظیمات لاگ برای مشاهده وضعیت در پنل Railway
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)

# دریافت مقادیر از بخش Variables در Railway
TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", 0))
TALK_THREAD_ID = int(os.getenv("TALK_THREAD_ID", 0))
RUNNING_THREAD_ID = int(os.getenv("RUNNING_THREAD_ID", 0))

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    # ثبت لاگ برای عیب‌یابی (نمایش آیدی گروه و تاپیک در کنسول)
    logging.info(f"Message received | Chat: {message.chat.id} | Topic: {message.message_thread_id}")

    # ۱. چک کردن اینکه پیام حتماً در گروه مورد نظر باشد
    if message.chat.id != GROUP_ID:
        return

    # ۲. چک کردن اینکه پیام در یکی از دو تاپیک مشخص شده باشد
    if message.message_thread_id not in [TALK_THREAD_ID, RUNNING_THREAD_ID]:
        return

    try:
        # ۳. بررسی وضعیت ادمین بودن فرستنده (پیام ادمین‌ها پاک نمی‌شود)
        member = await context.bot.get_chat_member(GROUP_ID, message.from_user.id)
        if member.status in ["administrator", "creator"]:
            return 
            
        # ۴. عملیات حذف پیام کاربر معمولی
        await message.delete()

        # ۵. ارسال پیام هشدار (با رعایت فاصله و علامت مورد نظر شما)
        warn_msg = await context.bot.send_message(
            chat_id=GROUP_ID,
            text="⛔ این تاپیک فقط برای اطلاع‌رسانی می‌باشد ⛔️",
            message_thread_id=message.message_thread_id
        )

        # ۶. حذف خودکار پیام هشدار بعد از ۲ ثانیه برای تمیز ماندن تاپیک
        await asyncio.sleep(2)
        await warn_msg.delete()

    except Exception as e:
        logging.error(f"Error in execution: {e}")

if __name__ == '__main__':
    if not TOKEN:
        logging.error("BOT_TOKEN is missing in Variables!")
    else:
        # راه‌اندازی اپلیکیشن ربات
        app = ApplicationBuilder().token(TOKEN).build()
        
        # تعریف هندلر برای پیام‌های متنی (به جز دستورات)
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_messages))

        logging.info("--- Bot is starting... ---")
        
        # اجرای دائمی ربات و نادیده گرفتن پیام‌های زمان خاموشی
        app.run_polling(drop_pending_updates=True)
