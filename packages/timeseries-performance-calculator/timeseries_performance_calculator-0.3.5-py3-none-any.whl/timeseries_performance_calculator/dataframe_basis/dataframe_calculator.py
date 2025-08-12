import pandas as pd
from timeseries_performance_calculator.basis import calculate_return
from universal_timeseries_transformer import PricesMatrix
from string_date_controller import get_ytd_date_pair_of_date_ref

def calculate_dataframe_cumreturns_between_dates(timeseries: pd.DataFrame, date_i: str, date_f: str = None, label_cumreturn:str = 'cumreturn') -> pd.DataFrame:
    date_f = date_f if date_f is not None else timeseries.index[-1]
    rows = timeseries.copy().loc[[date_i, date_f], :]
    rows.loc[label_cumreturn, :] = calculate_return(rows.iloc[0], rows.iloc[-1])
    return rows

def calculate_dataframe_cumreturns_ytd(timeseries: pd.DataFrame) -> pd.DataFrame:
    pm = PricesMatrix(timeseries)
    label = 'YTD'
    return calculate_dataframe_cumreturns_between_dates(timeseries, pm.historical_dates[label], pm.date_ref, label_cumreturn=label)

def calculate_dataframe_cumreturns_since_inception(timeseries: pd.DataFrame) -> pd.DataFrame:
    pm = PricesMatrix(timeseries)
    label = 'Since Inception'
    return calculate_dataframe_cumreturns_between_dates(timeseries, pm.historical_dates[label], pm.date_ref, label_cumreturn=label)

def get_cumreturns_row_between_dates(timeseries: pd.DataFrame, date_i: str, date_f: str = None, label_cumreturn:str = 'cumreturn') -> pd.DataFrame:
    table = calculate_dataframe_cumreturns_between_dates(timeseries, date_i, date_f, label_cumreturn)
    row = table.iloc[[-1]]
    row.index.name = 'period'
    return row

def get_cumreturns_row_ytd(timeseries: pd.DataFrame) -> pd.DataFrame:
    pm = PricesMatrix(timeseries)
    label = 'YTD'
    return get_cumreturns_row_between_dates(timeseries, pm.historical_dates[label], pm.date_ref, label_cumreturn=label)

def get_cumreturns_row_since_inception(timeseries: pd.DataFrame) -> pd.DataFrame:
    pm = PricesMatrix(timeseries)
    label = 'Since Inception'
    return get_cumreturns_row_between_dates(timeseries, pm.historical_dates[label], pm.date_ref, label_cumreturn=label)

def get_effective_date_ref(date_ref, year):
    if date_ref is None and year is None:
        raise ValueError('date_ref or year must be specified')
    elif date_ref is not None and year is not None:
        raise ValueError('date_ref and year cannot be specified at the same time')
    elif date_ref is None and year is not None:
        date_ref = f'{year}-01-01'
    elif date_ref is not None and year is None:
        pass
    return date_ref

def calculate_dataframe_cumreturns_ytd_of_year(timeseries: pd.DataFrame, date_ref: str=None, year: str=None) -> pd.DataFrame:
    pm = PricesMatrix(timeseries)
    date_ref = get_effective_date_ref(date_ref, year)
    date_ytd, date_year_end = get_ytd_date_pair_of_date_ref(dates=pm.dates, date_ref=date_ref)
    return calculate_dataframe_cumreturns_between_dates(timeseries, date_i=date_ytd, date_f=date_year_end, label_cumreturn='YTD')

def get_cumreturns_row_ytd_of_year(timeseries: pd.DataFrame, date_ref: str=None, year: str=None) -> pd.DataFrame:
    table = calculate_dataframe_cumreturns_ytd_of_year(timeseries, date_ref, year)
    row = table.iloc[[-1]]
    row.index.name = 'period'
    return row