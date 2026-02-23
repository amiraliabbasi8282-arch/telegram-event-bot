import os
import asyncio # برای ایجاد وقفه ۵ ثانیه‌ای
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# فرض کنید آیدی دو تاپیک را در تنظیمات Railway ذخیره کرده‌اید
TOPIC_ID_1 = int(os.getenv("TOPIC_ID_1", 0))
TOPIC_ID_2 = int(os.getenv("TOPIC_ID_2", 0))

async def enforcement_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # چک کردن اینکه آیا پیام در یکی از این دو تاپیک ارسال شده است
    current_topic = update.message.message_thread_id
    
    if current_topic in [TOPIC_ID_1, TOPIC_ID_2]:
        try:
            # ۱. حذف پیام کاربر
            await update.message.delete()
            
            # ۲. ارسال پیام هشدار ربات
            warning_text = "⛔️ این تاپیک مخصوص اطلاع رسانی می‌باشد ⛔️"
            sent_msg = await update.message.reply_text(warning_text)
            
            # ۳. انتظار به مدت ۵ ثانیه
            await asyncio.sleep(5)
            
            # ۴. حذف پیام خودِ ربات
            await sent_msg.delete()
            
        except Exception as e:
            print(f"Error in deleting: {e}")

# در بخش راه‌اندازی ربات
if __name__ == '__main__':
    application = ApplicationBuilder().token("YOUR_TOKEN").build()
    
    # هندلر برای شناسایی پیام‌های متنی در تاپیک‌ها
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), enforcement_handler))
    
    application.run_polling()
