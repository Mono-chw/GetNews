import logging
import psycopg2
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from the config.env file
load_dotenv('config.env')

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Database connection
def connect_db():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

# Function to store message in the database
def store_message(user_id, username, message_text, timestamp):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO telegram_messages (user_id, username, message_text, timestamp)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, username, message_text, timestamp))
        conn.commit()
    except Exception as e:
        logging.error(f"Error storing message: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# Command handler for /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send me a message and I will store it.')

# Message handler
def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    message_text = update.message.text
    timestamp = datetime.now()

    # Store the message in the database
    store_message(user_id, username, message_text, timestamp)

    update.message.reply_text('Message received and stored!')

def main():
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
