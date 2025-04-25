import requests
import os
import json
from datetime import datetime, timedelta
from database import CryptoPanicDB
from dotenv import load_dotenv
import schedule
import time
from dateutil import parser

# Load environment variables from the config.env file
load_dotenv('config.env')

# Now you can access the variables using os.getenv
api_key = os.getenv('CRYPTOPANIC_API_KEY')
db_name = os.getenv('DB_NAME')

class CryptoPanicCrawler:
    def __init__(self):
        self.api_key = api_key
        self.base_url = "https://cryptopanic.com/api/v1/posts/"
        self.db = CryptoPanicDB()
        self.latest_timestamp = None  # Track the latest timestamp

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

    def run(self, interval_minutes, max_iterations):
        print("爬虫启动...")
        iteration = 0
        self._fetch_and_save()
        schedule.every(interval_minutes).minutes.do(self._fetch_and_save)
        while True:
            schedule.run_pending()
            time.sleep(1)
            iteration += 1
            if max_iterations and iteration >= max_iterations:
                print("达到最大迭代次数，停止爬虫")
                break

    def _fetch_and_save(self):
        print(f"{datetime.now()} 开始抓取数据...")
        page = 1
        # Calculate the date for 24 hours ago
        one_day_ago = datetime.now() - timedelta(days=1)
        while True:
            params = {"filter": "hot", "page": page}
            if self.latest_timestamp:
                params["published_at"] = f">{self.latest_timestamp}"
            else:
                # Use the date for 24 hours ago as the initial filter
                params["published_at"] = f">{one_day_ago.isoformat()}"
            data = self.fetch_news(params=params)
            if data and data.get('results'):
                self.parse_news(data)
                print(f"已保存{len(data.get('results', []))}条新数据")
                # Update the latest timestamp
                self.latest_timestamp = max(
                    post['published_at'] for post in data.get('results', [])
                )
                page += 1
            else:
                print("未获取到有效数据或已到达最后一页")
                break
        print("本次抓取完成\n")

    def _insert_news(self, news_item):
        self.db.insert_news(news_item)

if __name__ == "__main__":
    crawler = CryptoPanicCrawler()
    crawler.run(15, 10)
