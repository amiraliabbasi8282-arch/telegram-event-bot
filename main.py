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
    # بررسی وجود پیام و اینکه آیا در تاپیک‌های مورد نظر ارسال شده است یا خیر
    if not update.message or update.message.message_thread_id not in [TOPIC_ID_1, TOPIC_ID_2]:
        return

    try:
        # دریافت اطلاعات فرستنده برای چک کردن سطح دسترسی
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id, user_id)

        # اگر فرستنده ادمین یا صاحب گروه بود، ربات هیچ واکنشی نشان نمی‌دهد
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return

        # برای کاربران معمولی:
        # الف) حذف پیام کاربر
        await update.message.delete()
        
        # ب) ارسال پیام هشدار
        warning_text = "⛔️ این تاپیک مخصوص اطلاع رسانی می‌باشد ⛔️"
        sent_msg = await update.message.reply_text(warning_text)
        
        # ج) ۲۰ ثانیه انتظار (طبق درخواست شما)
        await asyncio.sleep(20)
        
        # د) حذف پیام هشدار ربات
        await sent_msg.delete()
            
    except Exception as e:
        # چاپ خطا در لاگ‌های Railway برای عیب‌یابی
        print(f"Error in execution: {e}")

if __name__ == '__main__':
    # بررسی نهایی توکن قبل از اجرا
    if not TOKEN or TOKEN == "YOUR_TOKEN":
        print("❌ خطا: BOT_TOKEN در تنظیمات Railway تعریف نشده است.")
    else:
        # راه‌اندازی ربات
        application = ApplicationBuilder().token(TOKEN).build()
        
        # فعال کردن هندلر برای انواع پیام‌ها (متن، عکس، فایل و غیره)
        # این فیلتر باعث می‌شود تمام پیام‌های غیر از دستورات
