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
        # دریافت اطلاعات فرستنده
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id, user_id)

        # اگر فرستنده ادمین یا صاحب گروه بود، پیام پاک نشود
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return

        # برای کاربران معمولی:
        # الف) حذف پیام کاربر
        await update.message.delete()
        
        # ب) ارسال پیام هشدار به صورت بی‌صدا (بدون نوتیکیشن مزاحم)
        warning_text = "⛔️ این تاپیک مخصوص اطلاع رسانی می‌باشد ⛔️"
        sent_msg = await update.message.reply_text(
            warning_text, 
            disable_notification=True  # پیام بدون صدا ارسال می‌شود
        )
        
        # ج) ۲۰ ثانیه انتظار
        await asyncio.sleep(20)
        
        # د) حذف پیام ربات
        await sent_msg.delete()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    if not TOKEN or TOKEN == "YOUR_TOKEN":
        print("❌ خطا: BOT_TOKEN تنظیم نشده است.")
    else:
        application = ApplicationBuilder().token(TOKEN).build()
        
        # هندلر برای شناسایی تمام پیام‌ها در تاپیک‌ها
        application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), restricted_topic_handler))
        
        print("✅ ربات فعال شد. (حذف بعد از ۲۰ ثانیه + ارسال بی‌صدا)")
        application.run_polling()
