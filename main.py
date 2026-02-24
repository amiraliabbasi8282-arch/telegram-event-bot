import os
import asyncio
from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from datetime import timedelta

TOKEN = os.getenv("BOT_TOKEN")
IMAGE_THREAD_ID = int(os.getenv("IMAGE_THREAD_ID", 0))
GENERAL_THREAD_ID = int(os.getenv("GENERAL_THREAD_ID", 0))

# پاک کردن پیام غیرعکس در تاپیک image
async def image_only_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if update.message.message_thread_id != IMAGE_THREAD_ID:
        return

    if not update.message.photo:
        try:
            await update.message.delete()
        except:
            pass

# محدود کردن تاپیک‌های اطلاع‌رسانی
async def restricted_topic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if update.message.message_thread_id not in [GENERAL_THREAD_ID]:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    thread_id = update.message.message_thread_id

    member = await context.bot.get_chat_member(chat_id, user_id)

    if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return

    try:
        await update.message.delete()

        sent_msg = await context.bot.send_message(
            chat_id=chat_id,
            message_thread_id=thread_id,
            text="⛔️ این تاپیک مخصوص اطلاع رسانی می‌باشد ⛔️",
            disable_notification=True
        )

        await asyncio.sleep(1)

        await context.bot.delete_message(chat_id, sent_msg.message_id)

    except Exception as e:
        print(e)

if __name__ == '__main__':
    if not TOKEN:
        print("❌ BOT_TOKEN تنظیم نشده")
    else:
        application = ApplicationBuilder().token(TOKEN).build()

        application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), image_only_handler))
        application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), restricted_topic_handler))

        print("✅ ربات فعال شد")
        application.run_polling()
