import aiohttp
import asyncio
import requests
import pandas as pd
import numpy as np

async def fetch_fng_index():
    url = "https://api.alternative.me/fng/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            if data['data'] and len(data['data']) > 0:
                latest_data = data['data'][0]
                text = f"今日贪婪指数: {latest_data['value']}"
                # Send this text to your Telegram channel
                print(text)    

async def fetch_coingecko_trending():# API 请求地址
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_by_total_volume",
        "per_page": 10,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h",
        "locale": "en"
    }

    try:
        # 发送 GET 请求
        response = requests.get(url, params=params)
        
        # 检查请求是否成功
        if response.status_code == 200:
            data = response.json()
            
            # 提取关键信息
            crypto_data = []
            for coin in data:
                crypto_info = {
                    "名称": coin.get("id"),
                    "当前价格": f"${coin.get('current_price')}",
                    "24h涨跌幅": f"{coin.get('price_change_percentage_24h')}%",
                    "24h最高价": f"${coin.get('high_24h')}",
                    "24h最低价": f"${coin.get('low_24h')}",
                    "市值": f"${coin.get('market_cap')}",
                    "24h交易量": f"${coin.get('total_volume')}"
                }
                crypto_data.append(crypto_info)
            
            # 打印结果
            print("Top 10 加密货币数据：")
            for crypto in crypto_data:
                print(f"名称: {crypto['名称']}")
                print(f"当前价格: {crypto['当前价格']}")
                print(f"24小时涨跌幅: {crypto['24h涨跌幅']}")
                print(f"24小时最高价: {crypto['24h最高价']}")
                print(f"24小时最低价: {crypto['24h最低价']}")
                print(f"市值: {crypto['市值']}")
                print(f"24小时交易量: {crypto['24h交易量']}")
                print("-" * 40)
        else:
            print(f"请求失败，状态码: {response.status_code}")

    except Exception as e:
        print(f"发生错误: {str(e)}")

async def fetch_exchange_funding_rates():
    # 获取原始数据
    url = "https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(url)
    data = response.json()["symbols"]

    # 转换为结构化 DataFrame
    df = pd.DataFrame(data)

    # 展开嵌套的 filters 字段
    filters = pd.json_normalize(df["filters"].explode()).groupby(level=0).first()
    df = pd.concat([df, filters[["tickSize","minQty","maxQty","stepSize","minNotional"]]], axis=1)

    # 保留关键列
    cols = ["symbol","baseAsset","quoteAsset","status","orderTypes","permissions",
            "tickSize","minQty","maxQty","stepSize","minNotional"]
    df = df[cols]

    # 转换数值类型
    num_cols = ["tickSize","minQty","maxQty","stepSize","minNotional"]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")

    # 格式化显示（保留有效精度）
    pd.options.display.float_format = "{:.8f}".format

    # 添加可读性标签
    status_map = {"TRADING": "交易中", "BREAK": "暂停交易"}
    df["交易状态"] = df["status"].map(status_map)

    # 添加交易对类型分类
    df["交易类型"] = df["quoteAsset"].apply(lambda x: "稳定币" if x in ["USDT","BUSD"] else "其他")
            
    # 按报价资产分类统计
    quote_asset_stats = df.groupby("quoteAsset").agg(
        交易对数量=("symbol", "count"),
        最小交易量均值=("minQty", "mean"),
        最大交易量中位数=("maxQty", "median")
    ).sort_values("交易对数量", ascending=False)
    print(quote_asset_stats)
    # 交易状态分布
    status_dist = df["交易状态"].value_counts(normalize=True).apply(lambda x: f"{x:.1%}")
    print(status_dist)

    # 价格精度分布
    tick_size_dist = df["tickSize"].apply(lambda x: f"10^{round(np.log10(x))}" if not np.isnan(x) else "NaN").value_counts()
    print(tick_size_dist)


# Run the async function
if __name__ == "__main__":
    asyncio.run(fetch_fng_index())
    asyncio.run(fetch_coingecko_trending())
    asyncio.run(fetch_exchange_funding_rates())

