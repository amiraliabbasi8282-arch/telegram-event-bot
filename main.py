import os
import asyncio
from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ۱. دریافت تنظیمات از متغیرهای محیطی Railway
TOKEN = os.getenv("BOT_TOKEN")
TOPIC_ID_1 = int(os.getenv("TOPIC_ID_1", 0))
TOPIC_ID_2 = int(os.getenv("TOPIC_ID_2", 0))

async def restricted_topic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # بررسی وجود پیام و مطابقت با تاپیک‌های مورد نظر
    if not update.message or update.message.message_thread_id not in [TOPIC_ID_1, TOPIC_ID_2]:
        return

    try:
        # دریافت اطلاعات فرستنده و چت
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        thread_id = update.message.message_thread_id
        
        # بررسی سطح دسترسی کاربر (ادمین‌ها و مالک گروه استثنا هستند)
        member = await context.bot.get_chat_member(chat_id, user_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return

        # الف) حذف پیام کاربر غیر ادمین
        await update.message.delete()
        
        # ب) ارسال پیام هشدار (بدون صدا و مستقیم به تاپیک)
        sent_msg = await context.bot.send_message(
            chat_id=chat_id,
            message_thread_id=thread_id,
            text="⛔️ این تاپیک مخصوص اطلاع رسانی می‌باشد ⛔️",
            disable_notification=True
        )
        
        # ج) ۲.۵ ثانیه انتظار (تغییر طبق درخواست شما)
        await asyncio.sleep(2.5)
        
        # د) حذف پیام هشدار ربات بعد از ۲.۵ ثانیه
        await context.bot.delete_message(chat_id=chat_id, message_id=sent_msg.message_id)
            
    except Exception as e:
        print(f"Error logic: {e}")

if __name__ == '__main__':
    if not TOKEN or TOKEN == "YOUR_TOKEN":
        print("❌ خطا: BOT_TOKEN تنظیم نشده است.")
    else:
        application = ApplicationBuilder().token(TOKEN).build()
        
        # هندلر برای تمامی پیام‌ها (متن، عکس و...)
        application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), restricted_topic_handler))
        
        print("✅ ربات فعال شد. (حذف هشدار بعد از ۲.۵ ثانیه | ارسال بی‌صدا)")
        application.run_polling()
