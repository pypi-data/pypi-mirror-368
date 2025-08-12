import pandas as pd
from functools import partial
from universal_timeseries_transformer import PricesMatrix
from timeseries_performance_calculator.tables.table_utils import show_table_performance
from timeseries_performance_calculator.basis.return_calculator import calculate_return
from .table_functionals import map_prices_to_table_iterated_returns

# def map_prices_to_table_period_returns(prices: pd.DataFrame) -> pd.DataFrame:
#     pm = PricesMatrix(prices)

#     def create_table(label, date):
#         columns = pm.rows_by_names((date, pm.date_ref)).T
#         returns = calculate_return(columns.iloc[:, 0], columns.iloc[:, -1])
#         return returns.to_frame(label)
    
#     tables = [create_table(label, date) 
#               for label, date in pm.historical_dates.items()]
#     return pd.concat(tables, axis=1)

map_prices_to_table_period_returns = partial(map_prices_to_table_iterated_returns, option_iterated='period')
get_table_period_returns = map_prices_to_table_period_returns
show_table_period_returns = partial(show_table_performance, map_prices_to_table_period_returns)
