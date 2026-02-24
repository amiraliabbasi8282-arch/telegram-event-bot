import os
import asyncio
from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ---------------- Variables from Railway ----------------
TOKEN = os.getenv("BOT_TOKEN")

# نام تاپیک‌ها یا کلمات کلیدی که پیام‌ها باید در آن‌ها محدود شوند
TOPICS = os.getenv("TOPICS", "running,e").lower().split(",")  # مثال: "running,e"

# ---------------- Handler ----------------
async def restricted_topics_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # متن پیام یا عنوان گروه/چت
    text = (update.message.text or "").lower()
    chat_title = (update.message.chat.title or "").lower()

    # بررسی اینکه پیام متعلق به تاپیک محدود است
    if not any(topic.strip() in chat_title or topic.strip() in text for topic in TOPICS):
        return

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
            text="⛔️ این تاپیک فقط مخصوص اطلاع‌رسانی است ⛔️",
            disable_notification=True
        )
        await asyncio.sleep(1)
        await context.bot.delete_message(chat_id, warning.message_id)

        print(f"Deleted message from user {user_id} in chat {chat_title}")

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
