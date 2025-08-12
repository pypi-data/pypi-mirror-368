import pandas as pd
from functools import partial
from string_date_controller import MAPPING_MONTHS
from canonical_transformer import map_number_to_signed_string, map_signed_string_to_number
from timeseries_performance_calculator.functionals import pipe
from .monthly_returns_table import map_prices_to_table_monthly_returns, style_table_year_monthly

def map_prices_to_table_monthly_relative(prices, name_benchmark=None, option_round=None):
    if name_benchmark is None:
        name_benchmark = prices.columns[1]
    df = map_prices_to_table_monthly_returns(prices).copy()
    index_to_keep = [0, df.index.get_loc(name_benchmark)]
    df = df.iloc[index_to_keep, :]
    if option_round:
        df = df.map(lambda value: map_number_to_signed_string(value=value, decimal_digits=option_round))
        df = df.map(lambda value: map_signed_string_to_number(value=value))
    df.loc['relative', :] = df.T.iloc[:, 0] - df.T.iloc[:, -1]
    return df

def map_table_monthly_relative_to_tables(table_monthly_relative):
    columns = table_monthly_relative.columns
    years = sorted(set([year_month.split('-')[0] for year_month in columns]))
    tables = [table_monthly_relative.loc[:, [year_month for year_month in columns if year_month.split('-')[0] == year]] for year in years]
    return tables

style_table_monthly_relative = style_table_year_monthly

def map_prices_to_tables_monthly_relative(prices, name_benchmark=None, option_round=None, option_signed=False, option_rename_index=False):
    tables = pipe(
        partial(map_prices_to_table_monthly_relative, name_benchmark=name_benchmark, option_round=option_round),
        map_table_monthly_relative_to_tables,
    )(prices)
    return [style_table_monthly_relative(table, option_round=option_round, option_signed=option_signed, option_rename_index=option_rename_index) for table in tables]

get_tables_monthly_relative = map_prices_to_tables_monthly_relative    
show_tables_monthly_relative = partial(map_prices_to_tables_monthly_relative, option_round=4, option_signed=True, option_rename_index=True)

def show_table_monthly_relative_by_year(prices, name_benchmark=None, year=None, option_round=4, option_signed=True, option_rename_index=True):
    tables = map_prices_to_tables_monthly_relative(prices, name_benchmark=name_benchmark, option_round=option_round, option_signed=option_signed, option_rename_index=option_rename_index)
    years = [table.columns.name for table in tables]
    dct = dict(zip(years, tables))
    if year is None:
        return tables[-1]
    return dct[year]       

# def get_table_relative_seasonality(prices, index=-1):
#     df = map_prices_to_table_monthly_relative(prices).iloc[[index]]
#     df = df.T
#     df['year'] = df.index.map(lambda x: x.split('-')[0])
#     df['month'] = df.index.map(lambda x: x.split('-')[1])
#     df = df.pivot(index='year', columns='month', values=df.columns[0]).sort_index(ascending=False).dropna(axis=0, how='all')
#     df.loc['average: month', :] = df.mean(axis=0)
#     df.loc[:, 'average: year'] = df.mean(axis=1)
#     return df