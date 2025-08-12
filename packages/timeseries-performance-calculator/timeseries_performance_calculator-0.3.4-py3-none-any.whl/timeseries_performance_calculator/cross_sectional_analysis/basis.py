from typing import Callable
import pandas as pd
from universal_timeseries_transformer import decompose_timeserieses_to_list_of_timeserieses
from timeseries_performance_calculator.tables.yearly_returns_table import get_table_yearly_relative
from timeseries_performance_calculator.tables.total.total_performance_table import get_table_total_performance
from .parser import order_canonically_prices_rows, get_component_prices_in_prices, get_benchmark_price_in_prices


def get_crosssectional_result(kernel: Callable, prices: pd.DataFrame) -> pd.DataFrame:
    prices_ordered = order_canonically_prices_rows(prices)
    lst_of_prices = decompose_timeserieses_to_list_of_timeserieses(prices_ordered)
    dfs = [kernel(price) for price in lst_of_prices]
    return pd.concat(dfs)

def get_crosssectional_yearly_relative_by_components(component_prices: list[pd.DataFrame], benchmark_price: pd.DataFrame) -> pd.DataFrame:
    dfs = []
    for price in component_prices:
        df = get_table_yearly_relative(price.join(benchmark_price))
        index_ref = df.index[0]
        df = df.iloc[[-1]]
        df.index = [f'{index_ref} (benchmark: {benchmark_price.columns[0]})']
        dfs.append(df)
    return pd.concat(dfs)

map_components_to_crosssectional_yearly_relative = get_crosssectional_yearly_relative_by_components

def get_crosssectional_benchmark_result_by_components(kernel: Callable, component_prices: list[pd.DataFrame], benchmark_price: pd.DataFrame) -> pd.DataFrame:
    dfs = []
    for price in component_prices:
        df = kernel(price.join(benchmark_price)).iloc[[0]]
        df.index = [f'{price.columns[0]} (benchmark: {benchmark_price.columns[0]})']
        dfs.append(df)
    return pd.concat(dfs)

def get_crosssectional_benchmark_result(kernel: Callable, prices: pd.DataFrame, benchmark_index: int = -1, benchmark_name: str = None) -> pd.DataFrame:
    component_prices = get_component_prices_in_prices(prices, benchmark_index, benchmark_name)
    benchmark_price = get_benchmark_price_in_prices(prices, benchmark_index, benchmark_name)
    return get_crosssectional_benchmark_result_by_components(kernel, component_prices, benchmark_price)

def get_crosssectional_total_performance_by_components(component_prices: list[pd.DataFrame], benchmark_price: pd.DataFrame, free_returns: pd.DataFrame= None) -> pd.DataFrame:
    dfs = []
    for i, price in enumerate(component_prices):
        df = get_table_total_performance(price.join(benchmark_price), free_returns=free_returns)
        if i == 0:
            row_bm = df.iloc[[-1]]
        dfs.append(df.iloc[[0]])
    return pd.concat([*dfs, row_bm])

map_components_to_crosssectional_total_performance = get_crosssectional_total_performance_by_components
