import ccxt
from datetime import datetime, timedelta, timezone
import concurrent.futures
import pandas as pd
from throttled import Throttled, rate_limiter
from tenacity import retry, stop_after_attempt, wait_exponential

throttle = {
    "funding": Throttled(
        quota=rate_limiter.per_duration(limit=5, duration=timedelta(seconds=1)),
        timeout=1,
    ),
}


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
def public_get_public_funding_rate_history(exchange: ccxt.okx, params: dict):
    """
    Fetch funding rate history from the exchange.
    """
    throttle["funding"].limit(key="/funding")
    res = exchange.public_get_public_funding_rate_history(params=params)

    if not res.get("code") == "0":
        raise Exception(res.get("msg"))

    data = res.get("data")
    if not data:
        return []

    new_data = [
        dict(
            item,
            realFundingTime=datetime.fromtimestamp(
                int(int(item.get("fundingTime")) / 1000), tz=timezone.utc
            ),
        )
        for item in data
    ]
    return sorted(new_data, key=lambda x: x.get("fundingTime"))


def fetch_funding_rate_history(exchange: ccxt.okx, instId: str, since: int | datetime):
    if isinstance(since, datetime):
        since = int(since.timestamp() * 1000)

    fundings = []
    before = since
    while True:
        params = {
            "instId": instId,
            "before": before,
        }
        new_data = public_get_public_funding_rate_history(exchange, params)

        if not new_data:
            break

        fundings.extend(new_data)
        before = int(new_data[-1].get("fundingTime")) + 1

    return fundings

def get_okx_symbols(exchange: ccxt.okx, instType: str, quote: str):
    res = exchange.public_get_public_instruments(params={"instType": instType})
    return [item['instId'] for item in res['data'] if item['settleCcy'] == quote and item['state'] == 'live']


def df_funding_rate(exchange: ccxt.okx, symbols: list[str] | str, since: int | datetime):
    if isinstance(symbols, str):
        symbols = [symbols]

    res = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch_funding_rate_history, exchange, symbol, since)
            for symbol in symbols
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                rates = future.result()
                res.extend(rates)
            except Exception as e:
                print(f"Error fetching funding rates for {future}: {e}")
    df = pd.DataFrame(res)
    df['fundingTime'] = df['fundingTime'].astype(int)
    df['fundingRate'] = df['fundingRate'].astype(float)

    df['timestamp'] = (df['fundingTime'] / 1000).astype(int)
    df = df.pivot(index="timestamp", columns="instId", values="fundingRate")
    df.index = pd.to_datetime(df.index, unit="s", utc=True)
    return df


def main():
    exchange = ccxt.okx()

    # Example usage
    symbols = get_okx_symbols(exchange, 'SWAP', 'USDT')
    since = datetime.now() - timedelta(days=60)
    df = df_funding_rate(exchange, symbols, since)
    print(df)

if __name__ == "__main__":
    main()
