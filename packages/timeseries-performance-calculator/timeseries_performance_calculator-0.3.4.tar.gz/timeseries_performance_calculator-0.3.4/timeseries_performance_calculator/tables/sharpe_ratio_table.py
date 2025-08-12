from functools import partial
from typing import Optional
import pandas as pd
from universal_timeseries_transformer import PricesMatrix
from timeseries_performance_calculator.functionals import pipe
from timeseries_performance_calculator.basis.sharpe_ratio_calculator import calculate_sharpe_ratio
from timeseries_performance_calculator.tables.table_utils import style_table

def map_prices_to_table_sharpe_ratio(prices: pd.DataFrame, free_returns: pd.DataFrame = None)-> pd.DataFrame:
    pm = PricesMatrix(prices)
    returns = pm.returns
    data = []
    for col in returns.columns:
        name = col.replace('return: ', '')
        sharpe_ratio = calculate_sharpe_ratio(returns = returns[[col]], free_returns=free_returns)
        datum = {'name': name, 'sharpe_ratio': sharpe_ratio}
        data.append(datum)
    table = pd.DataFrame(data).set_index('name').rename_axis(None)
    return table

get_table_sharpe_ratio = map_prices_to_table_sharpe_ratio

def show_table_sharpe_ratio(prices: pd.DataFrame, free_returns: pd.DataFrame = None, option_round: Optional[int] = 4, option_signed: bool = False, option_rename_index: bool = True) -> pd.DataFrame:
    style_table_with_options = partial(style_table, option_round=option_round, option_signed=option_signed, option_rename_index=option_rename_index)    
    return pipe(
        partial(map_prices_to_table_sharpe_ratio, free_returns=free_returns),
        style_table_with_options
    )(prices)
    
