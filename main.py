import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
EVENT_TOPIC_ID = int(os.getenv("EVENT_TOPIC_ID"))

async def delete_if_not_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    
    if message and message.message_thread_id == EVENT_TOPIC_ID:
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        member = await context.bot.get_chat_member(chat_id, user_id)
        
        if member.status not in ["administrator", "creator"]:
            await message.delete()

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, delete_if_not_admin))
app.run_polling()
