import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential
import concurrent.futures

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_single_page(symbol: str, start_time: int) -> list[dict]:
    """
    Fetch a single page of funding rate history for a given symbol starting from start_time (ms).
    """
    url = "https://api.hyperliquid.xyz/info"
    payload = {
        "type": "fundingHistory",
        "coin": symbol,
        "startTime": start_time
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    time.sleep(0.5)  # sleep to avoid rate limiting
    return response.json()


def fetch_funding_rate_history(symbol: str, since: int | datetime) -> list[dict]:
    """
    Retrieve the complete funding rate history for a given symbol from Hyperliquid since a timestamp.
    """
    if isinstance(since, datetime):
        since = int(since.timestamp() * 1000)

    all_data = []
    while True:
        data = fetch_single_page(symbol, since)
        if not data:
            break
        all_data.extend(data)

        if len(data) < 500:
            break
        since = int(data[-1]["time"]) + 1

    for item in all_data:
        item["symbol"] = item["coin"]
        item["fundingTime"] = int(item["time"])
    
    return all_data


def get_symbols() -> list[str]:
    """
    Get all available trading symbols on Hyperliquid, excluding delisted ones.
    """
    url = "https://api.hyperliquid.xyz/info"
    payload = {"type": "meta"}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    universe = data.get("universe", [])
    return [item["name"] for item in universe if not item.get("isDelisted", False)]


def df_funding_rate(symbols: list[str] | str, since: int | datetime) -> pd.DataFrame:
    """
    Convert funding rate history to a pivoted DataFrame.
    """
    if isinstance(symbols, str):
        symbols = [symbols]

    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch_funding_rate_history, symbol, since)
            for symbol in symbols
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.extend(result)
            except Exception as e:
                print(f"Error fetching data: {e}")

    df = pd.DataFrame(results)
    df["fundingTime"] = df["fundingTime"].astype(int)
    df["fundingRate"] = df["fundingRate"].astype(float)
    df["timestamp"] = (df["fundingTime"] / 1000).astype(int)
    df = df.pivot(index="timestamp", columns="symbol", values="fundingRate")
    df.index = pd.to_datetime(df.index, unit="s", utc=True)
    return df


def main():
    symbols = get_symbols()
    since = datetime.now() - timedelta(days=60)
    df = df_funding_rate(symbols, since)
    print(df)


if __name__ == "__main__":
    main()