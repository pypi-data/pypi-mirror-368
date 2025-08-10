import ccxt
from datetime import datetime, timedelta, timezone
import concurrent.futures
from typing import Literal
import pandas as pd
from throttled import Throttled, rate_limiter
from tenacity import retry, stop_after_attempt, wait_exponential

throttle = {
    "funding": Throttled(
        quota=rate_limiter.per_duration(limit=600, duration=timedelta(seconds=5)),
        timeout=1,
    ),
}


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
def public_get_v5_market_funding_history(exchange: ccxt.bybit, params: dict):
    """
    Retrieve funding rate history from Bybit exchange.

    Args:
        exchange (ccxt.bybit): The Bybit exchange instance from ccxt library
        params (dict): Dictionary containing the following parameters:
            - category (str, required): Product type. Valid values: 'linear', 'inverse'
            - symbol (str, required): Symbol name (e.g., 'BTCUSDT'), uppercase only
            - startTime (int, optional): The start timestamp in milliseconds
            - endTime (int, optional): The end timestamp in milliseconds
            - limit (int, optional): Limit for data size per page. Range: [1, 200]. Default: 200

    Returns:
        dict: Response from the Bybit API containing funding rate history data

    Raises:
        ccxt.BaseError: If the API request fails or returns an error
    """
    throttle["funding"].limit(key="/v5/market/funding/history")

    res = exchange.public_get_v5_market_funding_history(params=params)

    if not int(res.get("retCode")) == 0:
        raise Exception(res.get("retMsg"))

    data = res["result"].get("list", [])
    if not data:
        return []

    new_data = [
        dict(
            item,
            fundingTime=datetime.fromtimestamp(
                int(item.get("fundingRateTimestamp")) / 1000, tz=timezone.utc
            ),
        )
        for item in data
    ]

    return sorted(new_data, key=lambda x: x.get("fundingTime"))


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
def public_get_v5_market_kline(exchange: ccxt.bybit, params: dict):
    throttle["funding"].limit(key="/v5/market/kline")

    res = exchange.public_get_v5_market_kline(params=params)

    if not int(res.get("retCode")) == 0:
        raise Exception(res.get("retMsg"))

    data = res["result"].get("list", [])
    if not data:
        return []

    return sorted(data, key=lambda k: int(k[0]))


def fetch_klines(
    exchange: ccxt.bybit,
    symbol: str,
    interval: Literal[
        "1", "3", "5", "15", "30", "60", "120", "240", "360", "720", "D", "W", "M"
    ],
    since: int | datetime,
    category: str = "linear",
):
    if isinstance(since, datetime):
        start_time = int(since.timestamp() * 1000)

    end_time = int(datetime.now(timezone.utc).timestamp() * 1000)

    all_klines = []
    seen_timestamps: set[int] = set()
    prev_start_time: int | None = None
    while True:
        # Check for infinite loop condition
        if prev_start_time is not None and prev_start_time == start_time:
            break
        prev_start_time = start_time
        klines = public_get_v5_market_kline(
            exchange=exchange,
            params={
                "category": category,
                "symbol": symbol,
                "interval": interval,
                "start": start_time,
            },
        )
        # Sort klines by start time and filter out duplicates
        klines = [
            kline
            for kline in klines
            if int(kline[0]) not in seen_timestamps and int(kline[0]) < end_time
        ]
        all_klines.extend(klines)
        seen_timestamps.update(int(kline[0]) for kline in klines)
        # If no new klines were found, break
        if not klines:
            break
        # Update the start_time to fetch the next set of bars
        start_time = int(klines[-1][0]) + 1
        # No more bars to fetch if we've reached the end time
        if start_time >= end_time:
            break
    df = pd.DataFrame(
        all_klines,
        columns=["startTime", "open", "high", "low", "close", "volume", "turnover"],
    )
    df["timestamp"] = pd.to_datetime(df["startTime"].astype(int), unit="ms", utc=True)
    df["symbol"] = symbol
    df = df[
        ["timestamp", "symbol", "open", "high", "low", "close", "volume", "turnover"]
    ]
    # remove the last row
    df = df[:-1]
    return df


def fetch_funding_rate_history(
    exchange: ccxt.bybit, symbol: str, since: int | datetime, category: str = "linear"
):
    """
    Fetch funding rate history for a specific symbol from Bybit exchange.

    Args:
        exchange (ccxt.bybit): The Bybit exchange instance from ccxt library
        symbol (str): Symbol name (e.g., 'BTCUSDT'), uppercase only
        since (int | datetime, optional): Start timestamp in milliseconds or datetime object.
            Defaults to None, which fetches the last 60 days of data.

    Returns:
        list: List of funding rate history data
    """
    if isinstance(since, datetime):
        since = int(since.timestamp() * 1000)

    new_data = public_get_v5_market_funding_history(
        exchange,
        params={
            "category": category,
            "symbol": symbol,
        },
    )

    if int(new_data[0]["fundingRateTimestamp"]) <= since or len(new_data) < 200:
        return [item for item in new_data if int(item["fundingRateTimestamp"]) >= since]

    fundings = []
    fundings.extend(new_data)

    while True:
        params = {
            "category": category,
            "symbol": symbol,
            "endTime": int(new_data[0]["fundingRateTimestamp"]) - 1,
        }
        new_data = public_get_v5_market_funding_history(exchange, params)

        if not new_data:
            break

        if int(new_data[0]["fundingRateTimestamp"]) <= since or len(new_data) < 200:
            new_data = [
                item for item in new_data if int(item["fundingRateTimestamp"]) >= since
            ]
            fundings.extend(new_data)
            break

        fundings.extend(new_data)
    fundings = sorted(fundings, key=lambda x: x.get("fundingTime"))
    return fundings


def df_funding_rate(
    exchange: ccxt.bybit,
    symbols: list[str] | str,
    since: int | datetime,
    category: str = "linear",
):
    if isinstance(symbols, str):
        symbols = [symbols]

    res = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                fetch_funding_rate_history, exchange, symbol, since, category
            )
            for symbol in symbols
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                rates = future.result()
                res.extend(rates)
            except Exception as e:
                print(f"Error fetching funding rates for {future}: {e}")
    df = pd.DataFrame(res)
    df["fundingTime"] = df["fundingRateTimestamp"].astype(int)
    df["fundingRate"] = df["fundingRate"].astype(float)

    df["timestamp"] = (df["fundingTime"] / 1000).astype(int)
    df = df.pivot(index="timestamp", columns="symbol", values="fundingRate")
    df.index = pd.to_datetime(df.index, unit="s", utc=True)
    return df


def df_klines(
    exchange: ccxt.bybit,
    symbols: list[str] | str,
    interval: Literal[
        "1", "3", "5", "15", "30", "60", "120", "240", "360", "720", "D", "W", "M"
    ],
    since: int | datetime,
    category: str = "linear",
    value_column: Literal[
        "open", "high", "low", "close", "volume", "turnover"
    ] = "close",
):
    if isinstance(symbols, str):
        symbols = [symbols]

    all_dfs = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch_klines, exchange, symbol, interval, since, category)
            for symbol in symbols
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                df = future.result()
                all_dfs.append(df)
            except Exception as e:
                print(f"Error fetching klines for symbol: {e}")

    if not all_dfs:
        return pd.DataFrame()

    combined_df = pd.concat(all_dfs, ignore_index=True)

    # Convert value column to float
    combined_df[value_column] = combined_df[value_column].astype(float)

    # Pivot with timestamp as index and symbols as columns
    df = combined_df.pivot(index="timestamp", columns="symbol", values=value_column)
    return df


def get_bybit_symbols(exchange: ccxt.bybit, category: str, quote: str):
    """
    Get all symbols for a specific category from Bybit exchange.

    Args:
        exchange (ccxt.bybit): The Bybit exchange instance from ccxt library
        category (str): Product type. Valid values: 'linear', 'inverse'

    Returns:
        list: List of symbol names
    """
    res = exchange.public_get_v5_market_instruments_info(
        params={"category": category, "limit": 1000}
    )

    if not int(res.get("retCode")) == 0:
        raise Exception(res.get("retMsg"))

    data = res["result"].get("list", [])
    return [
        s["symbol"]
        for s in data
        if s.get("status") == "Trading"
        and s.get("quoteCoin") == quote.upper()
        and s.get("contractType") == "LinearPerpetual"
    ]


def main():
    exchange = ccxt.bybit()

    symbols = get_bybit_symbols(exchange, "linear", "USDT")
    since = datetime.now() - timedelta(days=60)

    df = df_klines(
        exchange, symbols=symbols, interval="D", since=since, value_column="turnover"
    )
    print(df)
    # for symbol in sorted(symbols):
    #     print(f"Fetching funding rates for {symbol}...")
    #     fetch_funding_rate_history(exchange, symbol, since)
    # fetch_funding_rate_history(exchange, "ANIMEUSDT", since)


if __name__ == "__main__":
    main()
