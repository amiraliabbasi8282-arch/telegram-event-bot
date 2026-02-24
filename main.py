import os
import asyncio
import logging
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# فعال کردن لاگ برای نمایش در کنسول Railway
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)

# دریافت متغیرها از Environment Variables
TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", 0))
TALK_THREAD_ID = int(os.getenv("TALK_THREAD_ID", 0))
RUNNING_THREAD_ID = int(os.getenv("RUNNING_THREAD_ID", 0))

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    # لاگ کردن برای اطمینان از دریافت پیام
    logging.info(f"Message received | Chat: {message.chat.id} | Topic: {message.message_thread_id}")

    # ۱. بررسی آیدی گروه
    if message.chat.id != GROUP_ID:
        return

    # ۲. بررسی آیدی تاپیک (Thread ID)
    if message.message_thread_id not in [TALK_THREAD_ID, RUNNING_THREAD_ID]:
        return

    # ۳. بررسی وضعیت ادمین بودن فرستنده
    try:
        member = await context.bot.get_chat_member(GROUP_ID, message.from_user.id)
        if member.status in ["administrator", "creator"]:
            return 
            
        # اگر کاربر ادمین نبود:
        await message.delete()

        # ارسال هشدار (بدون ریپلای، چون پیام اصلی پاک شده)
        warn_msg = await context.bot.send_message(
            chat_id=GROUP_ID,
            text="⛔ این تاپیک فقط برای اطلاع‌رسانی می‌باشد.",
            message_thread_id=message.message_thread_id
        )

        # حذف پیام ربات بعد از ۲ ثانیه
        await asyncio.sleep(2)
        await warn_msg.delete()

    except Exception as e:
        logging.error(f"Error in execution: {e}")

if __name__ == '__main__':
    if not TOKEN:
        logging.error("BOT_TOKEN found is empty!")
    else:
        # ساخت اپلیکیشن
        app = ApplicationBuilder().token(TOKEN).build()
        
        # هندلر برای تمام پیام‌های متنی (غیر از دستورات)
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_messages))

        logging.info("--- Bot is starting... ---")
        
        # اجرای ربات به صورت دائمی
        app.run_polling(drop_pending_updates=True)
