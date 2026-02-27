import os
import asyncio
import logging
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# تنظیمات لاگ برای Railway
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)

# دریافت متغیرها از Railway
TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", 0))
TALK_THREAD_ID = int(os.getenv("TALK_THREAD_ID", 0))
RUNNING_THREAD_ID = int(os.getenv("RUNNING_THREAD_ID", 0))

# تاپیک‌های مجاز برای کنترل
ALLOWED_THREADS = [TALK_THREAD_ID, RUNNING_THREAD_ID]

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    logging.info(
        f"Message received | Chat: {message.chat.id} | "
        f"Thread: {message.message_thread_id} | "
        f"User: {message.from_user.id}"
    )

    # فقط داخل گروه مشخص شده کار کن
    if message.chat.id != GROUP_ID:
        return

    # اگر تاپیک نداشت یا جزو لیست نبود کاری نکن
    if message.message_thread_id not in ALLOWED_THREADS:
        return

    try:
        # چک کردن ادمین بودن
        member = await context.bot.get_chat_member(GROUP_ID, message.from_user.id)
        if member.status in ["administrator", "creator"]:
            return

        # 🔥 مهم: قبل از حذف، thread_id ذخیره شود
        thread_id = message.message_thread_id

        # حذف پیام کاربر
        await message.delete()

        # ارسال هشدار
        warn_msg = await context.bot.send_message(
            chat_id=GROUP_ID,
            text="⛔ این تاپیک فقط برای اطلاع‌رسانی می‌باشد ⛔️",
            message_thread_id=thread_id
        )

        # حذف هشدار بعد از ۱ ثانیه
        await asyncio.sleep(1)
        await warn_msg.delete()

    except Exception as e:
        logging.error(f"Error: {e}")


if __name__ == '__main__':
    if not TOKEN:
        logging.error("BOT_TOKEN is missing!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()

        # 🔥 این خط همه نوع پیام رو می‌گیره
        app.add_handler(
            MessageHandler(
                filters.ALL & (~filters.StatusUpdate.ALL),
                handle_messages
            )
        )

        logging.info("Bot is running...")
        app.run_polling(drop_pending_updates=True)
