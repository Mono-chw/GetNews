import tweepy
import sys
import os
from tweepy.streaming import StreamResponse
from dotenv import load_dotenv
import psycopg2
from datetime import datetime

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv('../config.env')

# Database connection
def connect_db():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

# API 认证
client = tweepy.Client(
    bearer_token=os.getenv('YOUR_BEARER_TOKEN'),
    consumer_key=os.getenv('API_KEY'),
    consumer_secret=os.getenv('API_SECRET'),
    access_token=os.getenv('ACCESS_TOKEN'),
    access_token_secret=os.getenv('ACCESS_TOKEN_SECRET')
)

# 流式监控类
class TweetMonitor(tweepy.StreamingClient):
    def on_data(self, data):
        tweet = data.data
        user = data.includes['users'][0]
        print(f"新推文：{user.username} - {tweet.text}")
        # 触发后续处理
        self.process_tweet(tweet, user.username)
        return True

    def process_tweet(self, tweet, username):
        # Connect to the database
        conn = connect_db()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO tweets (tweet_id, username, text, created_at)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (
                tweet.id,
                username,
                tweet.text,
                datetime.now()
            ))
            conn.commit()
            print("Tweet stored successfully")
        except Exception as e:
            print(f"Error storing tweet: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

# 创建监控实例
stream = TweetMonitor(bearer_token=os.getenv('YOUR_BEARER_TOKEN'))

# 添加监控规则
stream.add_rules(tweepy.StreamRule("比特币 OR BTC lang:zh"))  # 中文比特币相关推文
stream.add_rules(tweepy.StreamRule("from:elonmusk"))          # 马斯克账号推文

# 启动监控
stream.filter(
    expansions=["author_id"],
    tweet_fields=["created_at", "public_metrics"],
    user_fields=["username"]
)