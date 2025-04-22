from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from flask import Flask
from threading import Thread
import os
import logging
import asyncio

# Config
BOT_TOKEN = os.getenv("BOT_TOKEN")
PUBLIC_CHANNEL = "@ethioegzam"
PRIVATE_CHANNEL_ID = -1002666249316

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app for keep-alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Subscription checker
async def is_user_subscribed(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(PUBLIC_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Error checking subscription: {e}")
        return False

# Background delete function
async def delete_later(bot: Bot, chat_id: int, message_id: int, delay: int = 300):
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot = context.bot

    if not context.args:
        await update.message.reply_text("Please use the correct link to access the file.")
        return

    raw_code = context.args[0]
    message_id = None

    # Extract message ID
    if raw_code.startswith("https://t.me/c/"):
        parts = raw_code.strip().split("/")
        if parts[-1].isdigit():
            message_id = int(parts[-1])
    elif raw_code.isdigit():
        message_id = int(raw_code)

    if not message_id:
        await update.message.reply_text("Invalid file link or code.")
        return

    # Check if the user is subscribed
    if not await is_user_subscribed(bot, user.id):
        await update.message.reply_text(
            f"📢 Please join our channel first:\nhttps://t.me/{PUBLIC_CHANNEL.lstrip('@')}\n\n"
            "Then click the link again to get your file."
        )
        return

    try:
        # Forward the file from private channel
        forwarded = await bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=PRIVATE_CHANNEL_ID,
            message_id=message_id
        )

        await update.message.reply_text("ℹ️ This file will be automatically deleted after 5 minutes due to copyright protection.")

        # Run delete in the background
        asyncio.create_task(delete_later(bot, forwarded.chat.id, forwarded.message_id))

    except Exception as e:
        logger.error(f"Failed to forward or delete message: {e}")
        await update.message.reply_text("❌ Couldn't retrieve the file. Please try again later.")

# Handle random text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"💡 Please use the file links from our channel:\nhttps://t.me/{PUBLIC_CHANNEL.lstrip('@')}"
    )

# Main runner
def main():
    Thread(target=run_flask).start()

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
