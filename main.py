import os
import asyncio
from datetime import timedelta
from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
    JobQueue,
)

# ---------------- Variables from Railway ----------------
TOKEN = os.getenv("BOT_TOKEN")
IMAGE_THREAD_ID = int(os.getenv("IMAGE_THREAD_ID", 0))
GENERAL_THREAD_ID = int(os.getenv("GENERAL_THREAD_ID", 0))
RUNNING_THREAD_ID = int(os.getenv("RUNNING_THREAD_ID", 0))
TALK_THREAD_ID = int(os.getenv("TALK_THREAD_ID", 0))

# ---------------- Store General Messages ----------------
general_messages = []  # store (chat_id, message_id) for deletion

# ---------------- Unified Handler ----------------
async def unified_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    thread_id = update.message.message_thread_id  # can be None

    # ---------------- IMAGE ----------------
    if thread_id == IMAGE_THREAD_ID:
        if not update.message.photo:
            try:
                await update.message.delete()
                print(f"Deleted non-photo message in IMAGE: {update.message.message_id}")
            except Exception as e:
                print(f"Error deleting IMAGE message: {e}")
        return

    # ---------------- RUNNING & TALK ----------------
    elif thread_id in [RUNNING_THREAD_ID, TALK_THREAD_ID]:
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return  # admins free
            await update.message.delete()
            warning = await context.bot.send_message(
                chat_id=chat_id,
                message_thread_id=thread_id,
                text="⛔️ این تاپیک فقط مخصوص اطلاع‌رسانی است ⛔️",
                disable_notification=True
            )
            await asyncio.sleep(1)
            await context.bot.delete_message(chat_id, warning.message_id)
            print(f"Deleted message in {thread_id} from user {user_id} and sent warning")
        except Exception as e:
            print(f"Error in RUNNING/TALK handler: {e}")
        return

    # ---------------- GENERAL ----------------
    elif thread_id == GENERAL_THREAD_ID:
        # store message for 10-day cleanup
        general_messages.append((chat_id, update.message.message_id))
        print(f"Stored GENERAL message {update.message.message_id}")
        return

    # ---------------- Fallback for messages without thread_id ----------------
    else:
        print(f"Message in chat {chat_id} with thread_id {thread_id} ignored")


# ---------------- Cleanup General Every 10 Days ----------------
async def cleanup_general(context: ContextTypes.DEFAULT_TYPE):
    global general_messages
    print("Starting 10-day cleanup for GENERAL...")
    for chat_id, message_id in general_messages:
        try:
            await context.bot.delete_message(chat_id, message_id)
        except Exception as e:
            print(f"Error deleting GENERAL message {message_id}: {e}")
    general_messages = []
    print("✅ GENERAL cleanup done")


# ---------------- Main ----------------
if __name__ == "__main__":
    if not TOKEN:
        print("❌ BOT_TOKEN تنظیم نشده")
    else:
        application = ApplicationBuilder().token(TOKEN).build()

        # unified handler for all messages
        application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), unified_handler))

        # schedule 10-day cleanup
        application.job_queue.run_repeating(
            cleanup_general,
            interval=timedelta(days=10),
            first=10
        )

        print("✅ ربات فعال شد")
        application.run_polling()
