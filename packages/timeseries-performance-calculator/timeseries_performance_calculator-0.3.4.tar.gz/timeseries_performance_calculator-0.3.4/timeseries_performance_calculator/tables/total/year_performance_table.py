from typing import Optional
import pandas as pd
from timeseries_performance_calculator.tables.monthly_relative_table import show_table_monthly_relative_by_year
from timeseries_performance_calculator.tables.yearly_returns_table import show_table_yearly_relative, show_table_yearly_relative_by_year
from timeseries_performance_calculator.tables.monthly_relative_table import show_tables_monthly_relative

def show_table_year(prices:pd.DataFrame, name_benchmark:Optional[str]=None, year:Optional[str]=None, option_round:Optional[int]=4, option_signed:bool=True, option_rename_index:bool=True):
    table_year_monthly = show_table_monthly_relative_by_year(prices, name_benchmark=name_benchmark, option_round=option_round, option_signed=option_signed, option_rename_index=option_rename_index, year=year)
    table_year_ytd = show_table_yearly_relative_by_year(prices, name_benchmark=name_benchmark, option_round=option_round, option_signed=option_signed, option_rename_index=option_rename_index, year=year)
    return table_year_monthly.join(table_year_ytd)

def show_tables_year(prices:pd.DataFrame, name_benchmark:Optional[str]=None, option_round:Optional[int]=4, option_signed:bool=True, option_rename_index:bool=True):
    tables_monthly = show_tables_monthly_relative(prices, name_benchmark=name_benchmark, option_round=option_round, option_signed=option_signed, option_rename_index=option_rename_index)
    table_ytd = show_table_yearly_relative(prices, name_benchmark=name_benchmark, option_round=option_round, option_signed=option_signed, option_rename_index=option_rename_index)
    return [table.join(table_ytd.iloc[:, idx]) for idx, table in enumerate(tables_monthly)]

def get_dfs_tables_year(prices:pd.DataFrame, name_benchmark:Optional[str]=None, option_round:Optional[int]=4, option_signed:bool=False, option_rename_index:bool=False):
    tables_year = show_tables_year(prices, name_benchmark=name_benchmark, option_round=option_round, option_signed=option_signed, option_rename_index=option_rename_index)
    dfs_tables_year = {}
    for table in tables_year:
        year = table.columns[-1]
        dfs_tables_year[year] = table
    return dfs_tables_year
