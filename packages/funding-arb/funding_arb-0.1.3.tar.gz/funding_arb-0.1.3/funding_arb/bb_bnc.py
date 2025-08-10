import ccxt
import numpy as np
import concurrent.futures
from datetime import datetime, timedelta
from funding_arb.bnc import get_symbols
from funding_arb.bnc import df_funding_rate as bnc_df_funding_rate
from funding_arb.bybit import df_klines as bybit_df_klines
from funding_arb.bybit import df_funding_rate as bybit_df_funding_rate


def bnc_bb_calculate(days: int = 35, max_n: int = 15, volume_threshold: float = 1_000_000, vol_days: int = 35, exclude_symbols: list[str] = None):
    exchange_bnc = ccxt.binance()
    exchange_bybit = ccxt.bybit()

    symbols_bnc = get_symbols(exchange_bnc, "USDT", "linear")
    symbols_bybit = get_symbols(exchange_bybit, "USDT", "linear")

    symbols = list(set(symbols_bnc) & set(symbols_bybit))
    if exclude_symbols:
        symbols = [symbol for symbol in symbols if symbol not in exclude_symbols]

    since = datetime.now() - timedelta(days=60)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_bnc = executor.submit(bnc_df_funding_rate, exchange_bnc, symbols, since)
        future_bybit = executor.submit(
            bybit_df_funding_rate, exchange_bybit, symbols, since
        )

        df_bnc = future_bnc.result()
        df_bybit = future_bybit.result()
    
    df_vol = bybit_df_klines(
        exchange=exchange_bybit,
        symbols=symbols,
        interval="D",
        since=since,
        value_column="turnover"
    )
    df_vol = df_vol.rolling(window=timedelta(days=vol_days)).mean()
    volume_filter = df_vol.iloc[-1] >= volume_threshold
    valid_symbols = volume_filter[volume_filter].index.to_list()


    bybit_is_nan = df_bybit.isna()
    bnc_is_nan = df_bnc.isna()

    df_bnc = df_bnc.resample("8h").sum()
    df_bybit = df_bybit.resample("8h").sum()
    df_bnc[bnc_is_nan] = np.nan
    df_bybit[bybit_is_nan] = np.nan

    df_funding = df_bnc - df_bybit
    df_alpha = df_funding.rolling(
        window=timedelta(days=days), min_periods=days * 3
    ).mean()

    row = df_alpha.iloc[-1]
    row = row[valid_symbols]
    top_max_n_symbols = row.abs().nlargest(max_n).index.to_list()
    data = {f"{k}-PERP": v for k, v in row[top_max_n_symbols].to_dict().items()}
    return data
