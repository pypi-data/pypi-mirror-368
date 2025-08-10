import ccxt
import numpy as np
import concurrent.futures
from datetime import datetime, timedelta
from funding_arb.bnc import get_symbols
from funding_arb.bnc import df_funding_rate as bnc_df_funding_rate


def bnc_dtdc_calculate(days: int = 35, max_n: int = 15, diff_threshold: float = 0.002, exclude_base: list[str] = None):
    """
    Calculate the funding rate difference between Bybit USDT and USDC perpetual contracts.

    Args:
        days: Number of days to calculate the rolling mean.
        max_n: Maximum number of symbols to return.
        diff_threshold: Threshold for the funding rate difference to consider.
        exclude_base: List of base currencies to exclude from the calculation. eg. ['BTC', 'ETH']
    """
    exchange_bnc = ccxt.binance()

    symbols_bnc_dt = get_symbols(exchange_bnc, "USDT", "linear")
    symbols_bnc_dc = get_symbols(exchange_bnc, "USDC", "linear")

    # Extract base currencies from the USDT and USDC symbols
    bnc_dt_base = [symbol.replace('USDT', '') for symbol in symbols_bnc_dt]
    bnc_dc_base = [symbol.replace('USDC', '') for symbol in symbols_bnc_dc]
    
    # Find common base currencies
    common_base = list(set(bnc_dt_base) & set(bnc_dc_base))

    if exclude_base:
        common_base = [base for base in common_base if base not in exclude_base]

    # Filter to only include symbols with base currencies that exist in both USDT and USDC pairs
    symbols_bnc_dt = [base + 'USDT' for base in common_base if base + 'USDT' in symbols_bnc_dt]
    symbols_bnc_dc = [base + 'USDC' for base in common_base if base + 'USDC' in symbols_bnc_dc]
    

    since = datetime.now() - timedelta(days=60)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_bnc_dt = executor.submit(bnc_df_funding_rate, exchange_bnc, symbols_bnc_dt, since)
        future_bnc_dc = executor.submit(bnc_df_funding_rate, exchange_bnc, symbols_bnc_dc, since)

        df_bnc_dt = future_bnc_dt.result()
        df_bnc_dc = future_bnc_dc.result()
        
    
    df_bnc_dt_is_nan = df_bnc_dt.isna()
    df_bnc_dc_is_nan = df_bnc_dc.isna()

    df_bnc_dt = df_bnc_dt.resample("8h").sum()
    df_bnc_dc = df_bnc_dc.resample("8h").sum()
    df_bnc_dt[df_bnc_dt_is_nan] = np.nan
    df_bnc_dc[df_bnc_dc_is_nan] = np.nan

    # remove the quote
    df_bnc_common_usdt_renamed = df_bnc_dt.copy()
    df_bnc_common_usdc_renamed = df_bnc_dc.copy()

    # Rename columns by removing the suffix
    df_bnc_common_usdt_renamed.columns = [col.replace('USDT', '') for col in df_bnc_dt.columns]
    df_bnc_common_usdc_renamed.columns = [col.replace('USDC', '') for col in df_bnc_dc.columns]


    df_funding = df_bnc_common_usdt_renamed - df_bnc_common_usdc_renamed
    df_funding[df_funding.abs() > diff_threshold] = 0
    df_alpha = df_funding.rolling(
        window=timedelta(days=days), min_periods=days * 3
    ).mean()

    row = df_alpha.iloc[-1]
    top_max_n_symbols = row.abs().nlargest(max_n).index.to_list()
    # data = {f"{k}-PERP": v for k, v in row[top_max_n_symbols].to_dict().items()}
    return row[top_max_n_symbols].to_dict()

if __name__ == "__main__":
    res = bnc_dtdc_calculate()
    print(res)
