from functools import partial
import pandas as pd
from timeseries_performance_calculator.tables.period_returns_table import get_table_period_returns
from timeseries_performance_calculator.tables.monthly_returns_table import get_table_monthly_returns
from timeseries_performance_calculator.tables.yearly_returns_table import get_table_yearly_returns
from timeseries_performance_calculator.tables.annualized_return_table import get_table_annualized_return_cagr, get_table_annualized_return_days
from timeseries_performance_calculator.tables.annualized_volatility_table import get_table_annualized_volatility
from timeseries_performance_calculator.tables.sharpe_ratio_table import get_table_sharpe_ratio
from timeseries_performance_calculator.tables.maxdrawdown_table import get_table_maxdrawdown
from timeseries_performance_calculator.tables.beta_table import get_table_beta_by_index
from timeseries_performance_calculator.tables.winning_ratio_table import get_table_winning_ratio_by_index
from timeseries_performance_calculator.tables.information_ratio_table import get_table_information_ratio_by_index
from timeseries_performance_calculator.tables.tracking_error_table import get_table_tracking_error_by_index
from .parser import get_component_prices_in_prices, get_benchmark_price_in_prices
from .basis import get_crosssectional_result, get_crosssectional_benchmark_result_by_components, get_crosssectional_benchmark_result, map_components_to_crosssectional_total_performance, map_components_to_crosssectional_yearly_relative


get_crosssectional_period_returns = partial(get_crosssectional_result, get_table_period_returns)
get_crosssectional_yearly_returns = partial(get_crosssectional_result, get_table_yearly_returns)
get_crosssectional_monthly_returns = partial(get_crosssectional_result, get_table_monthly_returns)
get_crosssectional_annualized_return_cagr = partial(get_crosssectional_result, get_table_annualized_return_cagr)
get_crosssectional_annualized_return_days = partial(get_crosssectional_result, get_table_annualized_return_days)
get_crosssectional_annualized_volatility = partial(get_crosssectional_result, get_table_annualized_volatility)
get_crosssectional_maxdrawdown = partial(get_crosssectional_result, get_table_maxdrawdown)
def get_crosssectional_sharpe_ratio(prices: pd.DataFrame, free_returns: pd.DataFrame= None) -> pd.DataFrame:
    kernel_table = partial(get_table_sharpe_ratio, free_returns=free_returns)
    return get_crosssectional_result(kernel_table, prices)

# get_crosssectional_sharpe_ratio = partial(get_crosssectional_result, get_table_sharpe_ratio)


get_crosssectional_beta_by_components = partial(get_crosssectional_benchmark_result_by_components, get_table_beta_by_index)
get_crosssectional_beta = partial(get_crosssectional_benchmark_result, get_table_beta_by_index)
get_crosssectional_winning_ratio_by_components = partial(get_crosssectional_benchmark_result_by_components, get_table_winning_ratio_by_index)
get_crosssectional_winning_ratio = partial(get_crosssectional_benchmark_result, get_table_winning_ratio_by_index)
get_crosssectional_information_ratio_by_components = partial(get_crosssectional_benchmark_result_by_components, get_table_information_ratio_by_index)
get_crosssectional_information_ratio = partial(get_crosssectional_benchmark_result, get_table_information_ratio_by_index)
get_crosssectional_tracking_error_by_components = partial(get_crosssectional_benchmark_result_by_components, get_table_tracking_error_by_index)
get_crosssectional_tracking_error = partial(get_crosssectional_benchmark_result, get_table_tracking_error_by_index)

def get_crosssectional_yearly_relative(prices: pd.DataFrame, benchmark_index: int = -1, benchmark_name: str = None) -> pd.DataFrame:
    component_prices = get_component_prices_in_prices(prices, benchmark_index, benchmark_name)
    benchmark_price = get_benchmark_price_in_prices(prices, benchmark_index, benchmark_name)
    return map_components_to_crosssectional_yearly_relative(component_prices, benchmark_price)

def get_crosssectional_total_performance(prices: pd.DataFrame, benchmark_index: int = -1, benchmark_name: str = None, free_returns: pd.DataFrame= None) -> pd.DataFrame:
    component_prices = get_component_prices_in_prices(prices, benchmark_index, benchmark_name)
    benchmark_price = get_benchmark_price_in_prices(prices, benchmark_index, benchmark_name)
    return map_components_to_crosssectional_total_performance(component_prices, benchmark_price, free_returns)

def get_crosssectional_total_performance_without_benchmark(component_prices: list[pd.DataFrame], free_returns: pd.DataFrame= None) -> pd.DataFrame:
    annualized_return_cagr = get_crosssectional_annualized_return_cagr(component_prices)
    annualized_return_days = get_crosssectional_annualized_return_days(component_prices)
    annualized_volatility = get_crosssectional_annualized_volatility(component_prices)
    maxdrawdown = get_crosssectional_maxdrawdown(component_prices)
    sharpe_ratio = get_crosssectional_sharpe_ratio(component_prices, free_returns=free_returns)
    return pd.concat([annualized_return_cagr, annualized_return_days, annualized_volatility, maxdrawdown, sharpe_ratio], axis=1)

def get_crosssectional_total_performance_with_benchmark(component_prices: list[pd.DataFrame], benchmark_price: pd.DataFrame) -> pd.DataFrame:
    beta = get_crosssectional_beta(component_prices, benchmark_price)
    winning_ratio = get_crosssectional_winning_ratio(component_prices, benchmark_price)
    information_ratio = get_crosssectional_information_ratio(component_prices, benchmark_price)
    tracking_error = get_crosssectional_tracking_error(component_prices, benchmark_price)
    return pd.concat([beta, winning_ratio, information_ratio, tracking_error], axis=1)