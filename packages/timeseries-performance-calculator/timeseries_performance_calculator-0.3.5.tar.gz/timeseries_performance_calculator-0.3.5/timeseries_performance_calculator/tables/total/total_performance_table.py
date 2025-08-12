import pandas as pd
from functools import partial
from timeseries_performance_calculator.tables.annualized_return_table import get_table_annualized_return_cagr, get_table_annualized_return_days
from timeseries_performance_calculator.tables.annualized_volatility_table import get_table_annualized_volatility
from timeseries_performance_calculator.tables.maxdrawdown_table import get_table_maxdrawdown
from timeseries_performance_calculator.tables.sharpe_ratio_table import get_table_sharpe_ratio
from timeseries_performance_calculator.tables.beta_table import get_table_beta_by_index
from timeseries_performance_calculator.tables.winning_ratio_table import get_table_winning_ratio_by_index
from timeseries_performance_calculator.tables.information_ratio_table import get_table_information_ratio_by_index
from timeseries_performance_calculator.tables.tracking_error_table import get_table_tracking_error_by_index
from timeseries_performance_calculator.tables.table_utils import show_table_performance

def map_prices_to_table_total_performance(prices: pd.DataFrame, free_returns: pd.DataFrame = None)-> pd.DataFrame:
    table_cagr = get_table_annualized_return_cagr(prices)
    table_days = get_table_annualized_return_days(prices)
    table_vol = get_table_annualized_volatility(prices)
    table_mdd = get_table_maxdrawdown(prices)
    table_sharpe = get_table_sharpe_ratio(prices, free_returns=free_returns)
    table_beta = get_table_beta_by_index(prices, index_benchmark=1)
    table_winning_ratio = get_table_winning_ratio_by_index(prices, index_benchmark=1)
    table_information_ratio = get_table_information_ratio_by_index(prices, index_benchmark=1)
    table_tracking_error = get_table_tracking_error_by_index(prices, index_benchmark=1)
    return pd.concat([table_cagr, table_days, table_vol, table_mdd, table_sharpe, table_beta, table_winning_ratio, table_information_ratio, table_tracking_error], axis=1)

get_table_total_performance = map_prices_to_table_total_performance
show_table_total_performance = partial(partial(show_table_performance, map_prices_to_table_total_performance), option_signed=False, option_rename_index=True)
