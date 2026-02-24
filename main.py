import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8791482006:AAEk4jX6-b7-qljFd9nXMkOtebePmzloAY8"
GROUP_ID = -1003856173368  # آیدی گروه

TALK_THREAD_ID = 372
RUNNING_THREAD_ID = 155

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    if message.chat.id != GROUP_ID:
        return

    # اگر داخل تاپیک مورد نظر نبود کاری نکن
    if message.message_thread_id not in [TALK_THREAD_ID, RUNNING_THREAD_ID]:
        return

    member = await context.bot.get_chat_member(GROUP_ID, message.from_user.id)

    # اگر ادمین نبود
    if member.status not in ["administrator", "creator"]:
        try:
            await message.delete()

            warn_msg = await context.bot.send_message(
                chat_id=GROUP_ID,
                text="⛔️ این تاپیک برای اطلاع رسانی می‌باشد⛔️",
                message_thread_id=message.message_thread_id
            )

            await asyncio.sleep(1)
            await warn_msg.delete()

        except:
            pass


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, handle_messages))

print("Bot is running...")
app.run_polling()
