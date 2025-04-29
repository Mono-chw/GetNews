from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import aiohttp

# Import your functions for each task
from fetch_from_crypto_api import fetch_fng_index, fetch_coingecko_trending, fetch_exchange_funding_rates
#from twitter_monitor import monitor_twitter
from web3_news import CryptoPanicCrawler

async def main():
    scheduler = AsyncIOScheduler()

    # Schedule the Fear and Greed Index at 7 AM daily
    scheduler.add_job(fetch_fng_index, 'cron', hour=7)

    # Schedule Coingecko trending every 30 minutes
    scheduler.add_job(fetch_coingecko_trending, 'interval', minutes=30)

    # Schedule exchange funding rates every hour
    scheduler.add_job(fetch_exchange_funding_rates, 'interval', hours=1)

    # Schedule Web3 news fetching every 15 minutes
    scheduler.add_job(CryptoPanicCrawler().run, 'interval', minutes=15)

    scheduler.start()

    # Keep the script running
    await asyncio.Event().wait()

# Run the main function in the event loop
asyncio.run(main())
