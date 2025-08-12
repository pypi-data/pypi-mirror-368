import pandas as pd
from functools import partial
from timeseries_performance_calculator.basis import map_prices_to_maxdrawdowns
from timeseries_performance_calculator.functionals import pipe, map_dct_to_df, rename_column_with_label
from .table_utils import show_table_performance

def map_prices_to_table_maxdrawdown(prices: pd.DataFrame)-> pd.DataFrame:
    rename_column = partial(rename_column_with_label, 'maxdrawdown')
    return pipe(
        map_prices_to_maxdrawdowns,
        map_dct_to_df,
        rename_column,
    )(prices)

get_table_maxdrawdown = map_prices_to_table_maxdrawdown
show_table_maxdrawdown = partial(show_table_performance, get_table_maxdrawdown)
