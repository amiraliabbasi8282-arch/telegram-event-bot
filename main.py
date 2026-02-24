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
    user_id = update.effective_user.id

    try:
        member = await context.bot.get_chat_member(chat_id, user_id)

        # ادمین‌ها و مالک گروه مستثنا هستند
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return

        # حذف پیام کاربر
        await update.message.delete()

        # ارسال هشدار
        warning = await context.bot.send_message(
            chat_id=chat_id,
            message_thread_id=thread_id,
            text="⛔️ این تاپیک فقط مخصوص اطلاع‌رسانی است ⛔️",
            disable_notification=True
        )

        # ۱ ثانیه صبر
        await asyncio.sleep(1)

        # حذف هشدار
        await context.bot.delete_message(chat_id, warning.message_id)

    except Exception as e:
        print(e)

if __name__ == '__main__':
    if not TOKEN:
        print("❌ BOT_TOKEN تنظیم نشده")
    else:
        application = ApplicationBuilder().token(TOKEN).build()

        application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), image_only_handler))
        application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), restricted_topics_handler))

        print("✅ ربات فعال شد")
        application.run_polling()
