import os
import asyncio
from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from datetime import timedelta
from telegram.ext import CommandHandler, ContextTypes
from telegram import Update

# دستور دستی پاکسازی تاپیک image
async def cleanup_image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    image_thread = IMAGE_THREAD_ID

    await update.message.reply_text("شروع پاکسازی پیام‌های غیرعکسی در تاپیک image...")

    try:
        updates = await context.bot.get_chat_history(chat_id, limit=500, message_thread_id=image_thread)
        count = 0
        for message in updates:
            if not message.photo:  # فقط پیام‌هایی که عکس نیستند پاک میشن
                try:
                    await context.bot.delete_message(chat_id, message.message_id)
                    count += 1
                except:
                    pass
        await update.message.reply_text(f"پاکسازی تمام شد ✅ تعداد پیام‌های پاک شده: {count}")
    except Exception as e:
        await update.message.reply_text(f"خطا در پاکسازی: {e}")





# ۱. دریافت تنظیمات از متغیرهای محیطی Railway
TOKEN = os.getenv("BOT_TOKEN")
TOPIC_ID_1 = int(os.getenv("TOPIC_ID_1", 0))
TOPIC_ID_2 = int(os.getenv("TOPIC_ID_2", 0))

async def cleanup(context):
    chat_id = -1001234567890  # آیدی گروه
    image_thread = 238
    general_thread = 1

    # گرفتن آخرین پیام‌ها
    updates = await context.bot.get_chat_history(chat_id, limit=500, message_thread_id=image_thread)
    
    for message in updates:
        # اگر پیام **عکس نیست** پاک کن
        if not message.photo:
            try:
                await context.bot.delete_message(chat_id, message.message_id)
            except:
                pass
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
        
        # ج) ۱ ثانیه انتظار (تغییر طبق درخواست شما)
        await asyncio.sleep(1)
        
        # د) حذف پیام هشدار ربات بعد از ۱ ثانیه
        await context.bot.delete_message(chat_id=chat_id, message_id=sent_msg.message_id)
            
    except Exception as e:
        print(f"Error logic: {e}")

if __name__ == '__main__':
    if not TOKEN or TOKEN == "YOUR_TOKEN":
        print("❌ خطا: BOT_TOKEN تنظیم نشده است.")
    else:
        application = ApplicationBuilder().token(TOKEN).build()
       app.add_handler(CommandHandler("cleanup_image", cleanup_image_command))
        app.job_queue.run_repeating(
    cleanup,
    interval=timedelta(days=10),
    first=10
    )
        # هندلر برای تمامی پیام‌ها
        application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), restricted_topic_handler))
        
        print("✅ ربات فعال شد. (حذف هشدار بعد از ۱ ثانیه | ارسال بی‌صدا)")
        application.run_polling()
