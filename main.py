import os
import asyncio
from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ---------------- Variables from Railway ----------------
TOKEN = os.getenv("BOT_TOKEN")
RUNNING_THREAD_ID = int(os.getenv("RUNNING_THREAD_ID", 0))  # آیدی واقعی تاپیک Running
TALK_THREAD_ID = int(os.getenv("TALK_THREAD_ID", 0))        # آیدی واقعی تاپیک Talk

# ---------------- Handler ----------------
async def restricted_topics_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    thread_id = update.message.message_thread_id
    if thread_id not in [RUNNING_THREAD_ID, TALK_THREAD_ID]:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    try:
        # ادمین‌ها و مالک گروه استثنا هستند
        member = await context.bot.get_chat_member(chat_id, user_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return

        # حذف پیام کاربر
        await update.message.delete()

        # هشدار ۱ ثانیه‌ای
        warning = await context.bot.send_message(
            chat_id=chat_id,
            message_thread_id=thread_id,
            text="⛔️ این تاپیک فقط مخصوص اطلاع‌رسانی است ⛔️",
            disable_notification=True
        )
        await asyncio.sleep(1)
        await context.bot.delete_message(chat_id, warning.message_id)

        print(f"Deleted message from user {user_id} in thread {thread_id}")

    except Exception as e:
        print(f"Error handling message: {e}")

# ---------------- Main ----------------
if __name__ == "__main__":
    if not TOKEN:
        print("❌ BOT_TOKEN تنظیم نشده")
    else:
        application = ApplicationBuilder().token(TOKEN).build()
        application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), restricted_topics_handler))
        print("✅ ربات فعال شد")
        application.run_polling()
