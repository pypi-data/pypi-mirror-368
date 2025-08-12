import pandas as pd
from typing import Callable
from functools import partial
from universal_timeseries_transformer import PricesMatrix
from .basis import pipe
from .utils import rename_index, rename_column_with_kernel

map_prices_to_returns = lambda prices: PricesMatrix(prices).returns
map_prices_to_cumreturns = lambda prices: PricesMatrix(prices).cumreturns
map_srs_to_df = lambda srs: pd.DataFrame(srs)
map_dct_to_df = lambda dct: pd.DataFrame.from_dict(dct, orient='index')
map_timeseries_to_single_timeserieses = lambda timeseries: list(map(lambda col: timeseries[[col]], timeseries.columns))

def map_prices_to_performance_table(kernel_transformer: Callable, kernel_calculator: Callable, prices: pd.DataFrame)-> pd.DataFrame:
    map_prices_to_transformed = kernel_transformer
    map_transformed_to_srs = kernel_calculator
    rename_column = partial(rename_column_with_kernel, kernel_calculator)
    table = pipe(
        map_prices_to_transformed,
        map_transformed_to_srs,
        map_srs_to_df,
        rename_index,
        rename_column,
    )(prices)
    return table