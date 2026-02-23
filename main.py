import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ۱. دریافت تنظیمات از بخش Variables در Railway
TOKEN = os.getenv("BOT_TOKEN")
# در صورت نبود آیدی تاپیک، مقدار 0 در نظر گرفته می‌شود تا کد کرش نکند
TOPIC_ID_1 = int(os.getenv("TOPIC_ID_1", 0))
TOPIC_ID_2 = int(os.getenv("TOPIC_ID_2", 0))

async def restricted_topic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # بررسی اینکه آیا پیام در یکی از دو تاپیک مشخص شده ارسال شده است
    # و همچنین مطمئن می‌شویم که پیام از نوع "سیستمی" نیست
    if update.message and update.message.message_thread_id in [TOPIC_ID_1, TOPIC_ID_2]:
        try:
            # الف) پاک کردن پیام کاربر
            await update.message.delete()
            
            # ب) ارسال پیام هشدار
            warning_text = "⛔️ این تاپیک مخصوص اطلاع رسانی می‌باشد ⛔️"
            sent_msg = await update.message.reply_text(warning_text)
            
            # ج) ۵ ثانیه صبر
            await asyncio.sleep(5)
            
            # د) پاک کردن پیام خودِ ربات
            await sent_msg.delete()
            
        except Exception as e:
            print(f"Error in Topic Handler: {e}")

if __name__ == '__main__':
    # بررسی اینکه توکن حتماً مقدار داشته باشد
    if not TOKEN or TOKEN == "YOUR_TOKEN":
        print("❌ خطا: توکن ربات تنظیم نشده است! لطفا در Railway متغیر BOT_TOKEN را تعریف کنید.")
    else:
        # ۲. ساخت و اجرای ربات
        application = ApplicationBuilder().token(TOKEN).build()
        
        # تعریف هندلر برای تمام پیام‌های متنی (به جز دستورات)
        topic_check_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), restricted_topic_handler)
        application.add_handler(topic_check_handler)
        
        print("✅ ربات با موفقیت اجرا شد...")
        application.run_polling()
