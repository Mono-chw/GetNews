import requests
import os
import json
from datetime import datetime
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
            print("Processing post:", post)
            news_item = {
                'title': post.get('title'),
                'content': post.get('body'),
                'source_url': post.get('url'),
                'source': post.get('source', {}).get('domain'),
                'published_at': parser.isoparse(post['published_at']),
                # 修改这里：提取每个currency字典中的code值
                'tags': ', '.join(
                    [currency.get('code', 'none') for currency in post.get('currencies', [])]
                ) or 'none',  # 处理空列表的情况
                'votes': {
                    'positive': post.get('votes', {}).get('positive', 0),
                    'negative': post.get('votes', {}).get('negative', 0)
                }
            }
            self.db.insert_news(news_item)

    def run(self, interval_minutes=15):
        print("爬虫启动...")
        self._fetch_and_save()
        schedule.every(interval_minutes).minutes.do(self._fetch_and_save)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def _fetch_and_save(self):
        print(f"{datetime.now()} 开始抓取数据...")
        data = self.fetch_news(params={"filter": "hot"})  # 可选参数: rising/hot
        print(data)
        if data:
            self.parse_news(data)
            print(f"已保存{len(data.get('results', []))}条新数据")
        else:
            print("未获取到有效数据")
        print("本次抓取完成\n")

if __name__ == "__main__":
    crawler = CryptoPanicCrawler()
    crawler.run()
