import os
import asyncio
from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
TOPIC_ID_1 = int(os.getenv("TOPIC_ID_1", 0))
TOPIC_ID_2 = int(os.getenv("TOPIC_ID_2", 0))

async def restricted_topic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.message.message_thread_id not in [TOPIC_ID_1, TOPIC_ID_2]:
        return

    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        thread_id = update.message.message_thread_id
        
        member = await context.bot.get_chat_member(chat_id, user_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return

        # حذف پیام کاربر
        await update.message.delete()
        
        # ارسال پیام هشدار سایلنت (بدون صدا و لرزش)
        sent_msg = await context.bot.send_message(
            chat_id=chat_id,
            message_thread_id=thread_id,
            text="⛔️ این تاپیک مخصوص اطلاع رسانی می‌باشد ⛔️",
            disable_notification=True # این گزینه صدا را قطع می‌کند
        )
        
        await asyncio.sleep(10) # زمان انتظار ۱۰ ثانیه
        
        # حذف پیام ربات
        await context.bot.delete_message(chat_id=chat_id, message_id=sent_msg.message_id)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    if not TOKEN or TOKEN == "YOUR_TOKEN":
        print("❌ Error: BOT_TOKEN is missing!")
    else:
        application = ApplicationBuilder().token(TOKEN).build()
        application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), restricted_topic_handler))
        application.run_polling()
