import pandas as pd
from universal_timeseries_transformer import split_returns_to_pair_timeseries, split_timeseries_to_pair_timeseries
from .basis import validate_returns_with_benchmark

def calculate_tracking_error(returns):
    validate_returns_with_benchmark(returns)
    excess_return = returns.iloc[:, 0] - returns.iloc[:, 1] 
    tracking_error = excess_return.std()
    return tracking_error

def get_data_tracking_error_by_index(returns: pd.DataFrame, index: int, index_benchmark: int = 1) -> dict:
    returns_pair = split_timeseries_to_pair_timeseries(returns, index_benchmark=index_benchmark)[index]
    name = returns.columns[index].replace('return: ', '')
    tracking_error = calculate_tracking_error(returns_pair)
    return {'name': name, 'tracking_error': tracking_error}

def get_data_tracking_error_by_benchmark(returns: pd.DataFrame, name_benchmark: str) -> list[dict]:
    returns_pairs = split_returns_to_pair_timeseries(returns, name_benchmark=name_benchmark)
    
    def get_datum_tracking_error(returns_pair):
        name = returns_pair.columns[0].replace('return: ', '')
        tracking_error = calculate_tracking_error(returns_pair)
        return {'name': name, 'tracking_error': tracking_error}

    return [get_datum_tracking_error(returns_pair) for returns_pair in returns_pairs]