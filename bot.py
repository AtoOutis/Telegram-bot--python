from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Create a Flask app to keep the bot alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Function to keep Flask app running in a separate thread
def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Telegram bot handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello")

if __name__ == "__main__":
    # Run Flask in a separate thread
    thread = Thread(target=run_flask)
    thread.start()

    # Set up the Telegram bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()
