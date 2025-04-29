import aiohttp
import asyncio
import requests

# Your bot token
bot_token = '7823164292:AAH8eDJuoCJRxsmN2WwPTUX3sw-El01lUAQ'

# The channel ID
channel_id = '-1002651819121'  # Note the '-' prefix for channel IDs

# The URL for the Telegram API
telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

# The URL for the Fear and Greed Index API
fng_url = 'https://api.alternative.me/fng/'

async def main():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(fng_url) as response:
                data = await response.json()
                
                if data['data'] and len(data['data']) > 0:
                    latest_data = data['data'][0]
                    text = f"\n今日贪婪指数: {latest_data['value']}\n"
                    
                    # Send the message to the Telegram channel
                    payload = {
                        'chat_id': channel_id,
                        'text': text
                    }
                    async with session.post(telegram_url, data=payload) as telegram_response:
                        if telegram_response.status == 200:
                            print("Message sent successfully!")
                        else:
                            print(f"Failed to send message. Status code: {telegram_response.status}")
    except Exception as e:
        print('请求贪婪指数失败:', e)

# Run the async function
asyncio.run(main())