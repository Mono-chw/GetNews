import requests
import os
from dotenv import load_dotenv
import sys

# Load environment variables from the config.env file
load_dotenv('../config.env')

# Your bot token
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

# The channel ID
channel_id = '-1002651819121'  # Note the '-' prefix for channel IDs

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Function to send a message to a Telegram channel
def send_telegram_message(news_item):
    message = (
        f"Title: {news_item['title']}\n"
        f"Content: {news_item['content']}\n"
        f"Source URL: {news_item['source_url']}\n"
        f"Published At: {news_item['published_at']}\n"
        f"{'-' * 40}"
    )
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': channel_id,
        'text': message
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Message sent successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message: {e}")
