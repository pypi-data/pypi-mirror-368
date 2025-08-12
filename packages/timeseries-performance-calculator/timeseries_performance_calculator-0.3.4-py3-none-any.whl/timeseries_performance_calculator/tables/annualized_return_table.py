import pandas as pd
from typing import Callable, Optional
from functools import partial
from universal_timeseries_transformer import PricesMatrix
from timeseries_performance_calculator.basis import calculate_annualized_return_cagr, calculate_annualized_return_days
from timeseries_performance_calculator.functionals import pipe, rename_index, map_srs_to_df, rename_column_with_kernel
from .table_utils import show_table_performance

map_prices_to_cumreturns = lambda prices: PricesMatrix(prices).cumreturns
map_cumreturns_to_cumreturn_ref = lambda df: df.iloc[-1]
map_prices_to_trading_days = lambda prices: len(prices)

def map_prices_to_table_annualized_return(kernel: Callable[[pd.Series, int], pd.Series], prices: pd.DataFrame)-> pd.DataFrame:
    trading_days = map_prices_to_trading_days(prices)
    map_cumreturn_ref_to_srs = partial(kernel, trading_days=trading_days)
    rename_column = partial(rename_column_with_kernel, kernel)
    table = pipe(
        map_prices_to_cumreturns, 
        map_cumreturns_to_cumreturn_ref,
        map_cumreturn_ref_to_srs,
        map_srs_to_df,
        rename_column,
        rename_index,
    )(prices)
    return table

get_table_annualized_return_cagr = partial(map_prices_to_table_annualized_return, calculate_annualized_return_cagr)
get_table_annualized_return_days = partial(map_prices_to_table_annualized_return, calculate_annualized_return_days)
show_table_annualized_return_cagr = partial(show_table_performance, get_table_annualized_return_cagr)
show_table_annualized_return_days = partial(show_table_performance, get_table_annualized_return_days)
