import pandas as pd

def set_benchmark_index_in_prices(prices: pd.DataFrame, benchmark_index: int = -1, benchmark_name: str = None) -> int:
    cols = list(prices.columns)
    benchmark_index = cols.index(benchmark_name) if benchmark_name is not None else benchmark_index
    return benchmark_index

def order_canonically_prices_rows(prices: pd.DataFrame, benchmark_index: int = -1, benchmark_name: str = None) -> pd.DataFrame:
    component_prices = get_component_prices_in_prices(prices, benchmark_index, benchmark_name)
    benchmark_price = get_benchmark_price_in_prices(prices, benchmark_index, benchmark_name)
    return pd.concat([*component_prices, benchmark_price], axis=1)

def get_benchmark_price_in_prices(prices: pd.DataFrame, benchmark_index: int = -1, benchmark_name: str = None) -> pd.DataFrame:
    benchmark_index = set_benchmark_index_in_prices(prices, benchmark_index, benchmark_name)
    return prices.copy().iloc[:, [benchmark_index]]

def get_component_prices_in_prices(prices: pd.DataFrame, benchmark_index: int = -1, benchmark_name: str = None, option_dropna: bool = True) -> list[pd.DataFrame]:
    benchmark_index = set_benchmark_index_in_prices(prices, benchmark_index, benchmark_name)
    benchmark_col = prices.columns[benchmark_index]
    def dropna_rows_in_df(df, option_dropna=option_dropna):
        return df.dropna(axis=0) if option_dropna else df
    return [dropna_rows_in_df(prices[[col]]) for col in prices.columns if col != benchmark_col]
