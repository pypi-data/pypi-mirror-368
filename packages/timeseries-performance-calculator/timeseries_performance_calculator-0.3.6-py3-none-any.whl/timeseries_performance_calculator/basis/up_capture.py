import pandas as pd
from universal_timeseries_transformer import split_timeseries_to_pair_timeseries, split_returns_to_pair_timeseries
from .basis import validate_returns_with_benchmark

def calculate_up_capture(returns):
    validate_returns_with_benchmark(returns)
    up_returns_portfolio = returns[returns.iloc[:, 1] >= 0].iloc[:, 0]
    up_returns_benchmark = returns[returns.iloc[:, 1] >= 0].iloc[:, 1]
    up_capture = up_returns_portfolio.mean() / up_returns_benchmark.mean()
    return up_capture

def get_data_up_capture_by_index(returns: pd.DataFrame, index: int, index_benchmark: int = 1) -> dict:
    returns_pair = split_timeseries_to_pair_timeseries(returns, index_benchmark=index_benchmark)[index]
    name = returns.columns[index].replace('return: ', '')
    up_capture = calculate_up_capture(returns_pair)
    return {'name': name, 'up_capture': up_capture}

def get_data_up_capture_by_benchmark(returns: pd.DataFrame, name_benchmark: str) -> list[dict]:
    returns_pairs = split_returns_to_pair_timeseries(returns, name_benchmark=name_benchmark)
    
    def get_datum_up_capture(returns_pair):
        name = returns_pair.columns[0].replace('return: ', '')
        up_capture = calculate_up_capture(returns_pair)
        return {'name': name, 'up_capture': up_capture}

    return [get_datum_up_capture(returns_pair) for returns_pair in returns_pairs]
