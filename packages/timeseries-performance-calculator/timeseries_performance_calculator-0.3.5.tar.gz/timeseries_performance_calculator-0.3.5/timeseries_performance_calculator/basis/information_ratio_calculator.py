import pandas as pd
import numpy as np
from universal_timeseries_transformer import split_timeseries_to_pair_timeseries, split_returns_to_pair_timeseries
from .basis import validate_returns_with_benchmark
from .tracking_error_calculator import calculate_tracking_error

def calculate_information_ratio(returns):
    validate_returns_with_benchmark(returns)
    excess_return = returns.iloc[:, 0] - returns.iloc[:, 1] 
    tracking_error = excess_return.std()
    expected_excess_return = excess_return.mean()
    ANNUAL_TRADING_DAYS = 252
    annualized_expected_excess_return = expected_excess_return*ANNUAL_TRADING_DAYS
    annualized_tracking_error = tracking_error * np.sqrt(ANNUAL_TRADING_DAYS)
    information_ratio = annualized_expected_excess_return / annualized_tracking_error
    return information_ratio

def get_data_information_ratio_by_index(returns: pd.DataFrame, index: int, index_benchmark: int = 1) -> dict:
    returns_pair = split_timeseries_to_pair_timeseries(returns, index_benchmark=index_benchmark)[index]
    name = returns.columns[index].replace('return: ', '')
    information_ratio = calculate_information_ratio(returns_pair)
    return {'name': name, 'information_ratio': information_ratio}

def get_data_information_ratio_by_benchmark(returns: pd.DataFrame, name_benchmark: str) -> list[dict]:
    returns_pairs = split_returns_to_pair_timeseries(returns, name_benchmark=name_benchmark)
    
    def get_datum_information_ratio(returns_pair):
        name = returns_pair.columns[0].replace('return: ', '')
        information_ratio = calculate_information_ratio(returns_pair)
        return {'name': name, 'information_ratio': information_ratio}

    return [get_datum_information_ratio(returns_pair) for returns_pair in returns_pairs]