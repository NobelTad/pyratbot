from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = "7843150896:AAHpay0sUjwT2rclZ77PeO4yVRZLtbnb9nE"

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your bot. Type /help to see what I can do.")

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Available commands:\n/start - Welcome message\n/help - Show this help")

# Text message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower()

    if msg == "hi":
        await update.message.reply_text("Hello there, friend!")
    elif msg == "bye":
        await update.message.reply_text("Goodbye or see ya 👋")
    elif msg == "use":
        await update.message.reply_text("I'm just a test bot 🤖")
    else:
        await update.message.reply_text("I don't understand that. Try /help")

# Main function
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
