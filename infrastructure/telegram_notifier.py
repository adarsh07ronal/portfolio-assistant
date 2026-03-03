import requests
import os

class TelegramNotifier:
    def send(self, message: str):
        token = os.environ["TELEGRAM_TOKEN"]
        chat_id = os.environ["TELEGRAM_CHAT_ID"]

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message
        }

        requests.post(url, data=payload)