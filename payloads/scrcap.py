import os
from datetime import datetime
from PIL import ImageGrab

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