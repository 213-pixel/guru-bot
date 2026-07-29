import os
import requests
from dotenv import load_dotenv
from src.utils.logger import logger

load_dotenv()

def set_webhook():
    """Set webhook ke Telegram"""
    token = os.getenv("BOT_TOKEN")
    webhook_url = os.getenv("WEBHOOK_URL")
    
    if not token or not webhook_url:
        logger.error("BOT_TOKEN atau WEBHOOK_URL tidak ditemukan!")
        return
    
    # Tambahkan /webhook ke URL
    if not webhook_url.endswith("/webhook"):
        webhook_url = webhook_url.rstrip("/") + "/webhook"
    
    url = f"https://api.telegram.org/bot{token}/setWebhook"
    
    payload = {
        "url": webhook_url,
        "drop_pending_updates": True
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        if data.get("ok"):
            logger.info(f"✅ Webhook set successfully: {webhook_url}")
        else:
            logger.error(f"❌ Failed to set webhook: {data.get('description')}")
            
    except Exception as e:
        logger.error(f"❌ Error setting webhook: {e}")

def remove_webhook():
    """Hapus webhook (buat testing)"""
    token = os.getenv("BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/deleteWebhook"
    
    response = requests.post(url)
    if response.json().get("ok"):
        logger.info("✅ Webhook deleted")
    else:
        logger.error("❌ Failed to delete webhook")

if __name__ == "__main__":
    # Set webhook
    set_webhook()