from functools import partial
from canonical_transformer import map_number_to_signed_string, map_signed_string_to_number
from timeseries_performance_calculator.tables.table_utils import style_table, show_table_performance
from timeseries_performance_calculator.functionals import pipe
from .table_functionals import map_prices_to_table_iterated_returns

map_prices_to_table_yearly_returns = partial(map_prices_to_table_iterated_returns, option_iterated='yearly')
get_table_yearly_returns = map_prices_to_table_yearly_returns
show_table_yearly_returns = partial(show_table_performance, get_table_yearly_returns)

def map_prices_to_table_yearly_relative(prices, name_benchmark=None, option_round=None):
    if name_benchmark is None:
        name_benchmark = prices.columns[1]
    df = map_prices_to_table_yearly_returns(prices).copy()
    index_to_keep = [0, df.index.get_loc(name_benchmark)]
    df = df.iloc[index_to_keep, :]
    if option_round:
        df = df.map(lambda value: map_number_to_signed_string(value=value, decimal_digits=option_round))
        df = df.map(lambda value: map_signed_string_to_number(value=value))
    df.loc['relative', :] = df.T.iloc[:, 0] - df.T.iloc[:, -1]
    return df

get_table_yearly_relative = map_prices_to_table_yearly_relative

def show_table_yearly_relative(prices, name_benchmark=None, option_round=4, option_signed=True, option_rename_index=True):
    style_table_with_options = partial(style_table, option_round=option_round, option_signed=option_signed, option_rename_index=option_rename_index)
    return pipe(
        partial(map_prices_to_table_yearly_relative, name_benchmark=name_benchmark, option_round=option_round),
        style_table_with_options,
    )(prices)

def show_table_yearly_relative_by_year(prices, name_benchmark=None, year=None, option_round=4, option_signed=True, option_rename_index=True):
    table_ytds = show_table_yearly_relative(prices, name_benchmark=name_benchmark, option_round=option_round)
    table_ytd = table_ytds[year] if year is not None else table_ytds.iloc[:, -1]
    table_ytd = table_ytd.to_frame('YTD')
    return table_ytd
