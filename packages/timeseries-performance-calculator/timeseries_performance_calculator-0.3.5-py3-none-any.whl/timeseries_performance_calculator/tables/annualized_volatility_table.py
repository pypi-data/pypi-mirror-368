import pandas as pd
from functools import partial
from timeseries_performance_calculator.basis import calculate_annualized_volatility
from timeseries_performance_calculator.functionals import pipe, map_prices_to_returns, map_srs_to_df, rename_column_with_kernel, rename_index
from .table_utils import show_table_performance

def map_prices_to_table_annualized_volatility(prices: pd.DataFrame)-> pd.DataFrame:
    map_returns_to_srs = calculate_annualized_volatility
    rename_column = partial(rename_column_with_kernel, calculate_annualized_volatility)
    table = pipe(
        map_prices_to_returns,
        map_returns_to_srs,
        map_srs_to_df,
        rename_index,
        rename_column,
    )(prices)
    return table

get_table_annualized_volatility = map_prices_to_table_annualized_volatility
show_table_annualized_volatility = partial(show_table_performance, get_table_annualized_volatility)
