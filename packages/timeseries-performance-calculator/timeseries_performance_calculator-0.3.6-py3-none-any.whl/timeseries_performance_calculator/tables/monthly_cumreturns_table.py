from itertools import starmap
from typing import Union, Dict
import pandas as pd
from universal_timeseries_transformer import PricesMatrix
from string_date_controller import MAPPING_MONTHS
from canonical_transformer import map_number_to_signed_string, map_signed_string_to_number
from timeseries_performance_calculator.dataframe_basis.dataframe_calculator import get_cumreturns_row_between_dates, get_cumreturns_row_ytd_of_year
from timeseries_performance_calculator.consts import MAPPING_INDEX_NAMES

def get_monthly_cumreturns_table(prices: pd.DataFrame) -> pd.DataFrame:
    pm = PricesMatrix(prices)
    def extract_all_combinations(dct):
        return [
            (year, month, date_pair)
            for year, dct_months in dct.items()
            for month, date_pair in dct_months.items()
        ]
    
    def create_dataframe(year, month, date_pair):
        return get_cumreturns_row_between_dates(
            pm.df,
            date_i=date_pair[0],
            date_f=date_pair[1],
            label_cumreturn=f'{year}-{month}'
        )

    data_monthly_date_pairs = pm.monthly_date_pairs
    combinations = extract_all_combinations(data_monthly_date_pairs)
    dfs = starmap(create_dataframe, combinations)
    return pd.concat(dfs, axis=0)

def is_vaild_prices_with_benchmark(prices: pd.DataFrame) -> bool:
    return prices.shape[1] == 2

def get_prices_with_benchmark(prices: pd.DataFrame, benchmark_column: str) -> pd.DataFrame:
    prices = prices.copy()
    columns = prices.columns
    coulmns_to_keep = [0, columns.get_loc(benchmark_column)]
    prices_with_benchmark = prices.iloc[:, coulmns_to_keep]
    if not is_vaild_prices_with_benchmark(prices_with_benchmark):
        raise ValueError('prices_with_benchmark must have only 2 columns')
    return prices_with_benchmark

def add_indentifying_columns(df: pd.DataFrame) -> pd.DataFrame:
    df['year'] = df.index.str.split('-').str[0]
    df['month'] = df.index.str.split('-').str[1]
    return df

def get_data_of_grouped_dfs(df: pd.DataFrame) -> dict:
    return dict(tuple(df.groupby('year')))

def decorate_df_year(df: pd.DataFrame, year: str) -> pd.DataFrame:
    df = df.set_index('month')
    df = df.drop('year', axis=1)
    df.index.name = year
    return df

def get_data_cumreturns_tables_by_year(prices: pd.DataFrame) -> dict:
    df = get_monthly_cumreturns_table(prices)
    df = add_indentifying_columns(df)
    dct_dfs = get_data_of_grouped_dfs(df)
    dct = {}
    for year, df in dct_dfs.items():
        df = decorate_df_year(df, year)
        row_ytd = get_cumreturns_row_ytd_of_year(prices, year=year)
        df = pd.concat([row_ytd, df], axis=0)
        dct[year] = df
    return dct

def add_alpha_column(df: pd.DataFrame, decimal_digits: Union[int, None] = None) -> pd.DataFrame:        
    if is_vaild_prices_with_benchmark(df):
        df = df.map(lambda value: map_number_to_signed_string(value=value, decimal_digits=decimal_digits)) if decimal_digits is not None else df
        df = df.map(lambda value: map_signed_string_to_number(value=value)) if decimal_digits is not None else df
        df.loc[:, 'Alpha'] = df.iloc[:, 0] - df.iloc[:, 1]
    return df

def rename_month_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=MAPPING_MONTHS)
    return df

def extend_to_all_months(df: pd.DataFrame) -> pd.DataFrame:
    months = list(MAPPING_MONTHS.keys())
    months = months + ['YTD'] if 'YTD' in df.index else months
    df = df.reindex(months, axis=0)
    df = df.fillna('')
    return df

def preprocess_single_cumreturns_table_with_benchmark(prices_with_benchmark: pd.DataFrame, decimal_digits: Union[int, None] = None) -> pd.DataFrame:
    df = prices_with_benchmark.copy()
    df = (
        df
        .pipe(lambda df: add_alpha_column(df, decimal_digits))
        .pipe(lambda df: extend_to_all_months(df))
        .pipe(lambda df: df.T)
        .pipe(lambda df: rename_month_columns(df))
    )
    return df

def decorate_single_cumreturns_table_with_benchmark(df: pd.DataFrame) -> pd.DataFrame:
    index_renamed = list(df.index)
    index_renamed[0] = 'Fund'
    benchmark_indices = list(map(lambda x: MAPPING_INDEX_NAMES.get(x, x), index_renamed[1:]))
    index_renamed[1:] = benchmark_indices
    df.index = index_renamed
    return df

def transform_to_signed_numbers(df: pd.DataFrame, decimal_digits: int) -> pd.DataFrame:
    df = df.copy()
    df = df.map(lambda value: map_number_to_signed_string(value=value, decimal_digits=decimal_digits))
    return df

def show_monthly_cumreturns_table_with_benchmark(
    prices: pd.DataFrame, 
    benchmark_column: str, 
    decimal_digits: Union[int, None] = None, 
    option_signed: bool = True
) -> Dict[str, pd.DataFrame]:
    
    def process_dataframe(df):
        df = preprocess_single_cumreturns_table_with_benchmark(df, decimal_digits)
        df = decorate_single_cumreturns_table_with_benchmark(df)
        df = transform_to_signed_numbers(df, decimal_digits) if option_signed else df
        return df
    
    prices_with_benchmark = get_prices_with_benchmark(prices, benchmark_column)
    dct_dfs = get_data_cumreturns_tables_by_year(prices_with_benchmark)
    
    return {year: process_dataframe(df) for year, df in dct_dfs.items()}


    