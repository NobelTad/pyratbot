import platform
import socket
import psutil
import requests
import shutil
import screeninfo

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
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disk_info += f"\n[+] Device: {part.device}"
            disk_info += f"\n    Mountpoint: {part.mountpoint}"
            disk_info += f"\n    File System: {part.fstype}"
            disk_info += f"\n    Total Size: {round(usage.total / (1024 ** 3))} GB"
            disk_info += f"\n    Used: {round(usage.used / (1024 ** 3))} GB"
            disk_info += f"\n    Free: {round(usage.free / (1024 ** 3))} GB"
            disk_info += f"\n    Usage %: {usage.percent}"
        except PermissionError:
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