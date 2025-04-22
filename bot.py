from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from flask import Flask
from threading import Thread
import os
import telegram

BOT_TOKEN = os.getenv("BOT_TOKEN")

PUBLIC_CHANNEL = "@ethioegzam"
PRIVATE_CHANNEL_ID = -1002666249316  # Replace with your actual private channel ID

# Create a Flask app to keep the bot alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Function to keep Flask app running in a separate thread
def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Check if user is subscribed
async def is_user_subscribed(bot: telegram.Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(PUBLIC_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot = context.bot

    if context.args:
        code = context.args[0]
    else:
        await update.message.reply_text("Invalid or missing code.")
        return

    subscribed = await is_user_subscribed(bot, user.id)
    if not subscribed:
        await update.message.reply_text(f"Please join our channel first:\nhttps://t.me/{PUBLIC_CHANNEL.lstrip('@')}")
        return

    try:
        message_id = int(code)
        await bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=PRIVATE_CHANNEL_ID,
            message_id=message_id
        )
    except Exception as e:
        await update.message.reply_text("Sorry, the file could not be retrieved.")

# Fallback handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /start <code> to get your course material.")

if __name__ == "__main__":
    # Run Flask in a separate thread
    thread = Thread(target=run_flask)
    thread.start()

    # Set up the Telegram bot
    telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    telegram_app.run_polling()
