import requests

BOT_TOKEN = "7843150896:AAHpay0sUjwT2rclZ77PeO4yVRZLtbnb9nE"
CHAT_ID = "5441972884"  # Replace with your actual chat ID
TEXT = "Hello from your bot!"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": TEXT
}

response = requests.post(url, data=payload)
print(response.json())
