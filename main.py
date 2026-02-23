import os
import asyncio
from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ۱. دریافت تنظیمات از بخش Variables در Railway
TOKEN = os.getenv("BOT_TOKEN")
TOPIC_ID_1 = int(os.getenv("TOPIC_ID_1", 0))
TOPIC_ID_2 = int(os.getenv("TOPIC_ID_2", 0))

async def restricted_topic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # بررسی وجود پیام و مطابقت با تاپیک‌های مورد نظر
    if not update.message or update.message.message_thread_id not in [TOPIC_ID_1, TOPIC_ID_2]:
        return

    try:
        # دریافت اطلاعات کاربری فرستنده پیام
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id, user_id)

        # اگر کاربر ادمین یا صاحب گروه بود، کد را متوقف کن (پیام پاک نشود)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return

        # اگر کاربر معمولی بود:
        # الف) پاک کردن پیام کاربر
        await update.message.delete()
        
        # ب) ارسال پیام هشدار
        warning_text = "⛔️ این تاپیک مخصوص اطلاع رسانی می‌باشد ⛔️"
        sent_msg = await update.message.reply_text(warning_text)
        
        # ج) ۵ ثانیه انتظار
        await asyncio.sleep(5)
        
        # د) پاک کردن پیام ربات
        await sent_msg.delete()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    if not TOKEN or TOKEN == "YOUR_TOKEN":
        print("❌ خطا: توکن تنظیم نشده است.")
    else:
        application = ApplicationBuilder().token(TOKEN).build()
        
        # هندلر برای شناسایی تمام پیام‌ها (متن، عکس، ویدیو و غیره)
        # استفاده از filters.ALL باعث می‌شود حتی اگر کاربر عکس هم بفرستد، پاک شود
        application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), restricted_topic_handler))
        
        print("✅ ربات با قابلیت تشخیص ادمین فعال شد...")
        application.run_polling()
