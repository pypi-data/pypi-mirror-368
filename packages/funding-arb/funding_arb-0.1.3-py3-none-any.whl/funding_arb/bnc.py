import ccxt
from datetime import datetime, timedelta, timezone
import concurrent.futures
import pandas as pd
from throttled import Throttled, rate_limiter
from tenacity import retry, stop_after_attempt, wait_exponential


throttle = {
    "funding": Throttled(
        quota=rate_limiter.per_duration(limit=250, duration=timedelta(minutes=5)),
        timeout=1,
    ),
}

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
def fapi_public_get_funding_rate(exchange: ccxt.binance, params: dict):
    """
    Fetch funding rate history from Binance exchange.
    """
    throttle["funding"].limit(key="/fapi/v1/fundingRate")

    res = exchange.fapiPublicGetFundingRate(params=params)

    if not res:
        return []

    res = [{**item, "fundingTimestamp": item.pop("fundingTime")} for item in res]

    new_data = [
        dict(
            item,
            fundingTime=datetime.fromtimestamp(
                int(item.get("fundingTime")) / 1000, tz=timezone.utc
            ),
        )
        for item in res
    ]
    return sorted(new_data, key=lambda x: x.get("fundingTime"))


def fetch_funding_rate_history(
    exchange: ccxt.binance, symbol: str, since: int | datetime
):
    if isinstance(since, datetime):
        since = int(since.timestamp() * 1000)

    fundings = []
    while True:
        params = {
            "symbol": symbol.upper(),
            "startTime": since,
            "limit": 1000,
        }
        new_data = fapi_public_get_funding_rate(exchange, params)

        if not new_data:
            break

        if len(new_data) < 1000:
            # If we received less than the limit, we are done
            fundings.extend(new_data)
            break

        fundings.extend(new_data)
        since = int(new_data[-1].get("fundingTimestamp")) + 1

    return fundings


def df_funding_rate(
    exchange: ccxt.binance, symbols: list[str] | str, since: int | datetime
):
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
    df["fundingTime"] = df["fundingTimestamp"].astype(int)
    df["fundingRate"] = df["fundingRate"].astype(float)

    df["timestamp"] = (df["fundingTime"] / 1000).astype(int)
    df = df.pivot(index="timestamp", columns="symbol", values="fundingRate")
    df.index = pd.to_datetime(df.index, unit="s", utc=True)
    return df


def get_symbols(exchange: ccxt.binance, quote: str, type: str = "linear"):
    """
    Get all symbols from Binance that are trading against the specified quote currency.
    """
    markets = exchange.load_markets()
    return [
        market["id"]
        for market in markets.values()
        if market["quote"] == quote
        and market["active"]
        and market[type]
        and not market["future"]
        and not market["option"]
    ]

def main():
    exchange = ccxt.binance()
    symbols = get_symbols(exchange, "USDT", "linear")
    since = datetime.now() - timedelta(days=60)
    df = df_funding_rate(exchange, symbols, since)
    print(df)

if __name__ == "__main__":
    main()
