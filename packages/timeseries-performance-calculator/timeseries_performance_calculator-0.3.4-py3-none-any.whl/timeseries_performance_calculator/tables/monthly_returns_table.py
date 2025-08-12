from functools import partial
from string_date_controller import MAPPING_MONTHS
from timeseries_performance_calculator.tables.table_utils import style_table, show_table_performance
from timeseries_performance_calculator.functionals import pipe
from .table_functionals import map_prices_to_table_iterated_returns

map_prices_to_table_monthly_returns = partial(map_prices_to_table_iterated_returns, option_iterated='monthly')
get_table_monthly_returns = map_prices_to_table_monthly_returns
show_table_monthly_returns = partial(show_table_performance, get_table_monthly_returns)

def map_table_monthly_to_tables(table):
    columns = table.columns
    years = sorted(set([year_month.split('-')[0] for year_month in columns]))
    tables = [table.loc[:, [year_month for year_month in columns if year_month.split('-')[0] == year]] for year in years]
    return tables

def style_table_year_monthly(table, option_round=4, option_signed=True, option_rename_index=True):
    table = table.copy()
    table = style_table(table, option_round=option_round, option_signed=option_signed, option_rename_index=option_rename_index)
    year = table.columns[0].split('-')[0]
    table.columns = [MAPPING_MONTHS[year_month.split('-')[1]] for year_month in table.columns]
    table.columns.name = year
    table = table.T.reindex(MAPPING_MONTHS.values()).T.fillna('-')
    return table

def map_prices_to_tables_monthly_returns(prices, option_round=None, option_signed=False, option_rename_index=False):
    tables = pipe(
        partial(map_prices_to_table_monthly_returns),
        map_table_monthly_to_tables,
    )(prices)
    return [style_table_year_monthly(table, option_round=option_round, option_signed=option_signed, option_rename_index=option_rename_index) for table in tables]
    
show_tables_monthly_returns = partial(map_prices_to_tables_monthly_returns, option_round=4, option_signed=True, option_rename_index=True)

def get_table_seasonality(prices, index=0):
    df = map_prices_to_table_monthly_returns(prices).iloc[[index]]
    df = df.T
    df['year'] = df.index.map(lambda x: x.split('-')[0])
    df['month'] = df.index.map(lambda x: x.split('-')[1])
    df = df.pivot(index='year', columns='month', values=df.columns[0]).dropna(axis=0, how='all')
    df.loc['average: month', :] = df.mean(axis=0)
    df.loc[:, 'average: year'] = df.mean(axis=1)
    return df
