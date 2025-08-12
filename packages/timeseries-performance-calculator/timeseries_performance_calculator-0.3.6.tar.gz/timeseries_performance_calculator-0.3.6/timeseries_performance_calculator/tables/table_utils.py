import pandas as pd
from functools import partial
from typing import Union, Optional, Callable
from canonical_transformer import map_number_to_signed_string
from timeseries_performance_calculator.consts import MAPPING_INDEX_NAMES
from timeseries_performance_calculator.functionals import pipe

def validate_name_benchmark(name_benchmark: str, prices: pd.DataFrame) -> None:
    if name_benchmark not in prices.columns:
        raise ValueError(f"name_benchmark {name_benchmark} not found in prices")

def style_numbers(df: pd.DataFrame, option_round: Union[int, None] = None, option_signed: bool = False) -> pd.DataFrame:
    df = df.copy()
    if option_round is not None:
        df = df.map(lambda value: round(value, option_round))
    if option_signed:
        df = df.map(lambda value: map_number_to_signed_string(value=value, decimal_digits=option_round))
    return df

def rename_as_default_index_names(table: pd.DataFrame, option_rename_index: bool = True) -> pd.DataFrame:
    table = (
        table
        .copy()
        .rename(index=MAPPING_INDEX_NAMES)
        .rename(index=lambda idx: 'Fund' if (isinstance(idx, str) and len(idx) == 6 and any(c.isdigit() for c in idx)) else idx)
        # .rename(index={fund_code: 'Fund' for fund_code in get_fund_codes_all()})
    ) if option_rename_index else table
    return table

def style_table(table: pd.DataFrame, option_round: Optional[int] = 4, option_signed: bool = True, option_rename_index: bool = True):
    df = (
        table
        .copy()
        .pipe(partial(style_numbers, option_round=option_round, option_signed=option_signed))
        .pipe(partial(rename_as_default_index_names, option_rename_index=option_rename_index))
    )
    return df

def show_table_performance(kernel_table: Callable[[pd.DataFrame], pd.DataFrame], prices: pd.DataFrame, option_round: Optional[int] = 4, option_signed: bool = True, option_rename_index: bool = True) -> pd.DataFrame:
    style_table_with_options = partial(style_table, option_round=option_round, option_signed=option_signed, option_rename_index=option_rename_index)    
    return pipe(
        kernel_table,
        style_table_with_options
    )(prices)