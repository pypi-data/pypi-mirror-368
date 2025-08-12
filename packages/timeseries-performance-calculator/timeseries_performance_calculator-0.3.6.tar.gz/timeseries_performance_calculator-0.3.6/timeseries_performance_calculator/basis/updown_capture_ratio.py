import pandas as pd
from universal_timeseries_transformer import split_timeseries_to_pair_timeseries, split_returns_to_pair_timeseries
from .up_capture import calculate_up_capture
from .down_capture import calculate_down_capture

def calculate_updown_capture_ratio(returns):
    up_capture = calculate_up_capture(returns)
    down_capture = calculate_down_capture(returns)
    updown_capture_ratio = up_capture / down_capture
    return updown_capture_ratio

def get_data_updown_capture_ratio_by_index(returns: pd.DataFrame, index: int, index_benchmark: int = 1) -> dict:
    returns_pair = split_timeseries_to_pair_timeseries(returns, index_benchmark=index_benchmark)[index]
    name = returns.columns[index].replace('return: ', '')
    updown_capture_ratio = calculate_updown_capture_ratio(returns_pair)
    return {'name': name, 'updown_capture_ratio': updown_capture_ratio}

def get_data_updown_capture_ratio_by_benchmark(returns: pd.DataFrame, name_benchmark: str) -> list[dict]:
    returns_pairs = split_returns_to_pair_timeseries(returns, name_benchmark=name_benchmark)
    
    def get_datum_updown_capture_ratio(returns_pair):
        name = returns_pair.columns[0].replace('return: ', '')
        updown_capture_ratio = calculate_updown_capture_ratio(returns_pair)
        return {'name': name, 'updown_capture_ratio': updown_capture_ratio}

    return [get_datum_updown_capture_ratio(returns_pair) for returns_pair in returns_pairs]