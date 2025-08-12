import pandas as pd
import numpy as np
from universal_timeseries_transformer import split_timeseries_to_pair_timeseries, split_returns_to_pair_timeseries
from .basis import validate_returns_with_benchmark

def calculate_beta(returns: pd.DataFrame) -> float:
    validate_returns_with_benchmark(returns)
    return_portfolio = returns.iloc[:, 0]
    return_benchmark = returns.iloc[:, 1]
    return np.cov(return_portfolio, return_benchmark)[0][1] / np.var(return_benchmark)

def get_data_beta_by_index(returns: pd.DataFrame, index: int, index_benchmark: int = 1) -> dict:
    returns_pair = split_timeseries_to_pair_timeseries(returns, index_benchmark=index_benchmark)[index]
    name = returns.columns[index].replace('return: ', '')
    beta = calculate_beta(returns_pair)
    return {'name': name, 'beta': beta}

def get_data_beta_by_benchmark(returns: pd.DataFrame, name_benchmark: str) -> list[dict]:
    returns_pairs = split_returns_to_pair_timeseries(returns, name_benchmark=name_benchmark)
    
    def get_datum_beta(returns_pair):
        name = returns_pair.columns[0].replace('return: ', '')
        beta = calculate_beta(returns_pair)
        return {'name': name, 'beta': beta}

    return [get_datum_beta(returns_pair) for returns_pair in returns_pairs]