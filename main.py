import os
import asyncio
from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ---------------- Variables from Railway ----------------
TOKEN = os.getenv("BOT_TOKEN")
TOPIC_RUNNING = os.getenv("TOPIC_RUNNING", "").lower()  # اسم تاپیک Running
TOPIC_TALK = os.getenv("TOPIC_TALK", "").lower()        # اسم تاپیک Talk

# ---------------- Handler ----------------
async def restricted_topics_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    message_text = update.message.text or ""
    topic_title = (update.message.chat.title or "").lower()  # اسم گروه/تاپیک

    # بررسی اینکه پیام در تاپیک Running یا Talk است
    if TOPIC_RUNNING in topic_title or TOPIC_TALK in topic_title:
        try:
            # ادمین‌ها و مالک گروه استثنا هستند
            member = await context.bot.get_chat_member(chat_id, user_id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return

            # حذف پیام کاربر
            await update.message.delete()

            # ارسال هشدار ۱ ثانیه‌ای
            warning = await context.bot.send_message(
                chat_id=chat_id,
                text="⛔️ این تاپیک فقط مخصوص اطلاع‌رسانی است ⛔️",
                disable_notification=True
            )
            await asyncio.sleep(1)
            await context.bot.delete_message(chat_id, warning.message_id)

            print(f"Deleted message from user {user_id} in topic {topic_title}")

        except Exception as e:
            print(f"Error handling message: {e}")


# ---------------- Main ----------------
if __name__ == "__main__":
    if not TOKEN:
        print("❌ BOT_TOKEN تنظیم نشده")
    else:
        application = ApplicationBuilder().token(TOKEN).build()

        # هندلر برای تمام پیام‌ها
        application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), restricted_topics_handler))

        print("✅ ربات فعال شد")
        application.run_polling()
