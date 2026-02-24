import os
import asyncio
from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

IMAGE_THREAD_ID = int(os.getenv("IMAGE_THREAD_ID", 0))
GENERAL_THREAD_ID = int(os.getenv("GENERAL_THREAD_ID", 0))
RUNNING_THREAD_ID = int(os.getenv("RUNNING_THREAD_ID", 0))
TALK_THREAD_ID = int(os.getenv("TALK_THREAD_ID", 0))

# فقط عکس در تاپیک image مجاز است
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

# محدود کردن تاپیک‌های Running و Talk
async def restricted_topics_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    thread_id = update.message.message_thread_id

    if thread_id not in [RUNNING_THREAD_ID, TALK_THREAD_ID]:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user
