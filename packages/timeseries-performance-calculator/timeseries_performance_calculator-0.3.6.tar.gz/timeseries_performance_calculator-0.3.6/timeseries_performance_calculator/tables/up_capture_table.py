from functools import partial
from typing import Optional
import pandas as pd
import numpy as np
from universal_timeseries_transformer import PricesMatrix
from timeseries_performance_calculator.basis import get_data_up_capture_by_benchmark
from timeseries_performance_calculator.functionals import pipe
from .table_utils import style_table, validate_name_benchmark

def map_prices_and_name_to_table_up_capture(prices: pd.DataFrame, name_benchmark: str = None, option_self_manifest: bool = False) -> pd.DataFrame:
    name_benchmark = prices.columns[1] if name_benchmark is None else name_benchmark
    validate_name_benchmark(name_benchmark, prices)
    pm = PricesMatrix(prices)
    returns = pm.returns
    data = get_data_up_capture_by_benchmark(returns, name_benchmark)
    table = pd.DataFrame(data).set_index('name').rename_axis(None)
    if not option_self_manifest and name_benchmark in table.index:
        table.loc[name_benchmark, :] = np.nan 
    return table

def map_prices_and_index_to_table_up_capture(prices: pd.DataFrame, index_benchmark: int = 1, option_self_manifest: bool = False) -> pd.DataFrame:
    name_benchmark = prices.columns[index_benchmark]
    return map_prices_and_name_to_table_up_capture(prices, name_benchmark, option_self_manifest)

get_table_up_capture_by_benchmark = map_prices_and_name_to_table_up_capture
get_table_up_capture_by_index = map_prices_and_index_to_table_up_capture

def show_table_up_capture_by_index(prices: pd.DataFrame, index_benchmark: int = 1, option_self_manifest: bool = False, option_round: Optional[int] = 4, option_signed: bool = True, option_rename_index: bool = True) -> pd.DataFrame:
    style_table_with_options = partial(style_table, option_round=option_round, option_signed=option_signed, option_rename_index=option_rename_index)    
    return pipe(
        partial(map_prices_and_index_to_table_up_capture, index_benchmark=index_benchmark, option_self_manifest=option_self_manifest),
        style_table_with_options
    )(prices)
    
def show_table_up_capture_by_benchmark(prices: pd.DataFrame, name_benchmark: str = None, option_self_manifest: bool = False, option_round: Optional[int] = 4, option_signed: bool = False, option_rename_index: bool = True) -> pd.DataFrame:
    style_table_with_options = partial(style_table, option_round=option_round, option_signed=option_signed, option_rename_index=option_rename_index)    
    return pipe(
        partial(map_prices_and_name_to_table_up_capture, name_benchmark=name_benchmark, option_self_manifest=option_self_manifest),
        style_table_with_options
    )(prices)
    