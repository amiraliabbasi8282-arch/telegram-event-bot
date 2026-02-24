import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# گرفتن توکن و آیدی‌ها از Environment Variables
TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
TALK_THREAD_ID = int(os.getenv("TALK_THREAD_ID"))
RUNNING_THREAD_ID = int(os.getenv("RUNNING_THREAD_ID"))

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    # فقط داخل گروه مورد نظر
    if message.chat.id != GROUP_ID:
        return

    # فقط در تاپیک‌های مشخص
    if message.message_thread_id not in [TALK_THREAD_ID, RUNNING_THREAD_ID]:
        return

    # بررسی اینکه کاربر ادمین هست یا نه
    member = await context.bot.get_chat_member(GROUP_ID, message.from_user.id)
    if member.status not in ["administrator", "creator"]:
        try:
            # حذف پیام کاربر
            await message.delete()

            # ارسال هشدار کوتاه
            warn_msg = await context.bot.send_message(
                chat_id=GROUP_ID,
                text="⛔️ این تاپیک برای اطلاع رسانی می‌باشد⛔️",
                message_thread_id=message.message_thread_id
            )

            # حذف پیام ربات بعد از ۱ ثانیه
            await asyncio.sleep(1)
            await warn_msg.delete()

        except Exception as e:
            print("Error:", e)

# ساخت اپلیکیشن و افزودن هندلر
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, handle_messages))

print("Bot is running...")
app.run_polling()
