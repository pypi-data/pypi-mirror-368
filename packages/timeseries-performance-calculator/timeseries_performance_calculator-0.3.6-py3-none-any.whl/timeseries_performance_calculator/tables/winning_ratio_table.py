import pandas as pd
import numpy as np
from functools import partial
from timeseries_performance_calculator.basis.winning_ratio_calculator import calculate_winning_ratio
from timeseries_performance_calculator.functionals import pipe
from timeseries_performance_calculator.tables.table_utils import style_table

def map_prices_and_name_to_table_winning_ratio(prices: pd.DataFrame, name_benchmark: str, option_self_manifest: bool = False)-> pd.DataFrame:
    data = []
    for col in prices.columns:
        name = col
        winning_ratio = calculate_winning_ratio(prices = prices[[name, name_benchmark]]) if name != name_benchmark else np.nan
        datum = {'name': name, 'winning_ratio': winning_ratio}
        data.append(datum)
    table = pd.DataFrame(data).set_index('name').rename_axis(None)
    if not option_self_manifest and name_benchmark in table.index:
        table.loc[name_benchmark, :] = np.nan 
    return table

def map_prices_and_index_to_table_winning_ratio(prices: pd.DataFrame, index_benchmark: int = 1, option_self_manifest: bool = False)-> pd.DataFrame:
    name_benchmark = prices.columns[index_benchmark]
    return map_prices_and_name_to_table_winning_ratio(prices, name_benchmark, option_self_manifest)

get_table_winning_ratio_by_benchmark = map_prices_and_name_to_table_winning_ratio
get_table_winning_ratio_by_index = map_prices_and_index_to_table_winning_ratio

def show_table_winning_ratio_by_benchmark(prices: pd.DataFrame, name_benchmark: str, option_round: int = 4, option_signed: bool = False, option_rename_index: bool = True)-> pd.DataFrame:
    style_table_with_options = partial(style_table, option_round=option_round, option_signed=option_signed, option_rename_index=option_rename_index)    
    return pipe(
        partial(get_table_winning_ratio_by_benchmark, name_benchmark=name_benchmark),
        style_table_with_options
    )(prices)

def show_table_winning_ratio_by_index(prices: pd.DataFrame, index_benchmark: int = 1, option_round: int = 4, option_signed: bool = False, option_rename_index: bool = True)-> pd.DataFrame:
    style_table_with_options = partial(style_table, option_round=option_round, option_signed=option_signed, option_rename_index=option_rename_index)    
    return pipe(
        partial(get_table_winning_ratio_by_index, index_benchmark=index_benchmark),
        style_table_with_options
    )(prices)
    