import ccxt
import numpy as np
import concurrent.futures
from datetime import datetime, timedelta
from funding_arb.bybit import get_bybit_symbols
from funding_arb.bybit import df_funding_rate as bybit_df_funding_rate


def bb_dtdc_calculate(days: int = 35, max_n: int = 15, diff_threshold: float = 0.002, exclude_base: list[str] = None):
    """
    Calculate the funding rate difference between Bybit USDT and USDC perpetual contracts.

    Args:
        days: Number of days to calculate the rolling mean.
        max_n: Maximum number of symbols to return.
        diff_threshold: Threshold for the funding rate difference to consider.
        exclude_base: List of base currencies to exclude from the calculation. eg. ['BTC', 'ETH']
    """
    exchange_bybit = ccxt.bybit()

    # symbols_bybit_dt = get_bybit_symbols(exchange_bybit, "USDT", "linear")
    symbols_bybit_dt = get_bybit_symbols(exchange_bybit, quote="USDT", category="linear")
    symbols_bybit_dc = get_bybit_symbols(exchange_bybit, quote="USDC", category="linear") #NOTE: USE [USDC]
    
    
    # Extract base currencies from the USDT and USDC symbols
    bybit_dt_base = [symbol.replace('USDT', '') for symbol in symbols_bybit_dt]
    bybit_dc_base = [symbol.replace('PERP', '') for symbol in symbols_bybit_dc] #NOTE: USE [PERP]
    
    # Find common base currencies
    common_base = list(set(bybit_dt_base) & set(bybit_dc_base))
    if exclude_base:
        common_base = [base for base in common_base if base not in exclude_base]
    # print(common_base)
    # Filter to only include symbols with base currencies that exist in both USDT and USDC pairs
    symbols_bybit_dt = [base + 'USDT' for base in common_base if base + 'USDT' in symbols_bybit_dt]
    symbols_bybit_dc = [base + 'PERP' for base in common_base if base + 'PERP' in symbols_bybit_dc] #NOTE: USE [PERP]
    

    since = datetime.now() - timedelta(days=60)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_bybit_dt = executor.submit(bybit_df_funding_rate, exchange_bybit, symbols_bybit_dt, since)
        future_bybit_dc = executor.submit(bybit_df_funding_rate, exchange_bybit, symbols_bybit_dc, since)

        df_bybit_dt = future_bybit_dt.result()
        df_bybit_dc = future_bybit_dc.result()
        
    
    df_bybit_dt_is_nan = df_bybit_dt.isna()
    df_bybit_dc_is_nan = df_bybit_dc.isna()

    df_bybit_dt = df_bybit_dt.resample("8h").sum()
    df_bybit_dc = df_bybit_dc.resample("8h").sum()
    df_bybit_dt[df_bybit_dt_is_nan] = np.nan
    df_bybit_dc[df_bybit_dc_is_nan] = np.nan

    # remove the quote
    df_bybit_common_usdt_renamed = df_bybit_dt.copy()
    df_bybit_common_usdc_renamed = df_bybit_dc.copy()

    # Rename columns by removing the suffix
    df_bybit_common_usdt_renamed.columns = [col.replace('USDT', '') for col in df_bybit_dt.columns]
    df_bybit_common_usdc_renamed.columns = [col.replace('PERP', '') for col in df_bybit_dc.columns] #NOTE: USE [PERP]


    df_funding = df_bybit_common_usdt_renamed - df_bybit_common_usdc_renamed
    df_funding[df_funding.abs() > diff_threshold] = 0
    df_alpha = df_funding.rolling(
        window=timedelta(days=days), min_periods=days * 3
    ).mean()

    row = df_alpha.iloc[-1]
    top_max_n_symbols = row.abs().nlargest(max_n).index.to_list()
    # data = {f"{k}-PERP": v for k, v in row[top_max_n_symbols].to_dict().items()}
    return row[top_max_n_symbols].to_dict()

if __name__ == "__main__":
    res = bb_dtdc_calculate()
    print(res)
