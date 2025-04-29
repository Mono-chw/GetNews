import requests
import sys
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import schedule
import time
from dateutil import parser

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the send_telegram_message function
from tg_bot.msg_fwd_bot import send_telegram_message

import database

# Load environment variables from the config.env file
load_dotenv('../config.env')

# Now you can access the variables using os.getenv
api_key = os.getenv('CRYPTOPANIC_API_KEY')
db_name = os.getenv('DB_NAME')

class CryptoPanicCrawler:
    def __init__(self):
        self.api_key = api_key
        self.base_url = "https://cryptopanic.com/api/v1/posts/"
        self.db = database.CryptoPanicDB()

    def fetch_news(self, params=None):
        default_params = {
            "auth_token": self.api_key,
            "public": "true",
            "kind": "news"  # 可选 news/media
        }
        if params:
            default_params.update(params)
        
        try:
            response = requests.get(self.base_url, params=default_params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None

    def parse_news(self, data):
        print("Parsing news data...")
        for post in data.get('results', []):
            try:
                print("Processing post:", post)
                parsed_news = {
                    'title': post.get('title'),
                    'content': post.get('body'),
                    'source_url': post.get('url'),
                    'source': post.get('source', {}).get('domain'),
                    'published_at': parser.isoparse(post['published_at']),
                    'tags': ', '.join(
                        [currency.get('code', 'none') for currency in post.get('currencies', [])]
                    ) or 'none',
                    'votes': {
                        'positive': post.get('votes', {}).get('positive', 0),
                        'negative': post.get('votes', {}).get('negative', 0)
                    }
                }
                self._insert_news(parsed_news)
            except Exception as e:
                print(f"Failed to process post: {e}")

    def _fetch_and_save(self):
        print(f"{datetime.now()} 开始抓取数据...")
        # Calculate the date for 15 minutes ago
        fifteen_minutes_ago = datetime.now() - timedelta(minutes=15)
        params = {"filter": "hot", "published_at": f">{fifteen_minutes_ago.isoformat()}"}
        data = self.fetch_news(params=params)
        if data and data.get('results'):
            self.parse_news(data)
            print(f"已保存{len(data.get('results', []))}条新数据")
        else:
            print("未获取到有效数据")
        print("本次抓取完成\n")

    def run(self):
        self._fetch_and_save()

    def _insert_news(self, news_item):
        self.db.insert_news(news_item)
        # Call the function to send the news to Telegram
        send_telegram_message(news_item)

if __name__ == "__main__":
    crawler = CryptoPanicCrawler()
    crawler.run()