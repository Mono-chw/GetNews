import psycopg2
import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta

# Load environment variables from the config.env file
load_dotenv('config.env')

class CryptoPanicDB:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def insert_news(self, news_data):
        print("Inserting news data:", news_data)
        try:
            query = """
                INSERT INTO crypto_panic_news 
                (title, content, source_url, source, published_at, tags, votes_positive, votes_negative)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (
                news_data['title'],
                news_data['content'],
                news_data['source_url'],
                news_data['source'],
                news_data['published_at'],
                news_data.get('tags', 'none'),  # 添加 tags 字段
                news_data['votes']['positive'],
                news_data['votes']['negative']
))
            self.conn.commit()
            print("Data inserted successfully")
        except Exception as e:
            print(f"Database error: {e}")
            self.conn.rollback()

    def delete_old_entries(self):
        print("Deleting entries older than one week...")
        try:
            one_week_ago = datetime.now() - timedelta(weeks=1)
            query = """
                DELETE FROM crypto_panic_news 
                WHERE published_at < %s
            """
            self.cursor.execute(query, (one_week_ago,))
            self.conn.commit()
            print("Old entries deleted successfully")
        except Exception as e:
            print(f"Error deleting old entries: {e}")
            self.conn.rollback()

    def close(self):
        self.cursor.close()
        self.conn.close()