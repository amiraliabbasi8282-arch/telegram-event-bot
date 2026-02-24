import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# گرفتن توکن و آیدی‌ها از محیط (Environment Variables)
TOKEN = os.getenv("BOT_TOKEN")
# آیدی گروه باید با -100 شروع شود، مثلا: -100123456789
GROUP_ID = int(os.getenv("GROUP_ID", 0))
TALK_THREAD_ID = int(os.getenv("TALK_THREAD_ID", 0))
RUNNING_THREAD_ID = int(os.getenv("RUNNING_THREAD_ID", 0))

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    # لاگ برای عیب‌یابی (در کنسول Railway این‌ها را چک کن)
    print(f"Chat ID: {message.chat.id} | Topic ID: {message.message_thread_id}")

    # ۱. بررسی آیدی گروه
    if message.chat.id != GROUP_ID:
        return

    # ۲. بررسی آیدی تاپیک (Thread ID)
    # اگر در تاپیک General پیام می‌دهی، آیدی آن معمولاً 1 یا None است
    if message.message_thread_id not in [TALK_THREAD_ID, RUNNING_THREAD_ID]:
        return

    # ۳. بررسی وضعیت ادمین بودن فرستنده
    try:
        member = await context.bot.get_chat_member(GROUP_ID, message.from_user.id)
        if member.status in ["administrator", "creator"]:
            return # اگر ادمین بود، کاری انجام نده
            
        # اگر کاربر ادمین نبود:
        # حذف پیام کاربر
        await message.delete()

        # ارسال هشدار به همان تاپیک
        warn_msg = await context.bot.send_message(
            chat_id=GROUP_ID,
            text="⛔ این تاپیک فقط برای اطلاع‌رسانی می‌باشد.",
            message_thread_id=message.message_thread_id
        )

        # حذف پیام ربات بعد از ۲ ثانیه (زمان را کمی بیشتر کردم تا دیده شود)
        await asyncio.sleep(2)
        await warn_msg.delete()

    except Exception as e:
        print(f"Error in execution: {e}")

# ساخت و اجرای اپلیکیشن
if __name__ == '__main__':
    if not TOKEN:
        print("خطا: توکن ربات یافت نشد!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        
        # استفاده از فیلتر متن و حذف دستورات (/)
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_messages))

        print("Bot is running...")
        app.run_polling()
