import pandas as pd
from operator import getitem
from universal_timeseries_transformer import slice_timeseries_by_dates, PricesMatrix
from timeseries_performance_calculator.functionals import pipe, validate_single_timeseries, map_timeseries_to_single_timeserieses

map_prices_to_cumreturns = lambda prices: PricesMatrix(prices).cumreturns

def map_single_cumreturns_to_df_drawdown(cumreturns: pd.DataFrame)-> pd.DataFrame:
    df = validate_single_timeseries(cumreturns.copy())
    df['trough'] = df.iloc[:, 0]
    df['historical_peak'] = df['trough'].cummax()
    mapping_trough_to_date = df.reset_index().drop_duplicates('trough').set_index('trough')['date'].to_dict()
    df['date_peak'] = df['historical_peak'].map(mapping_trough_to_date)
    df['drawdown'] = ((df['trough'] + 100) / (df['historical_peak'] + 100) - 1)*100
    return df

def map_df_drawdown_to_data_maxdrawdown(df_drawdown: pd.DataFrame) -> dict:
    name = df_drawdown.columns[0].split(': ')[-1]  
    date_mdd = df_drawdown['drawdown'].idxmin()  
    row_mdd = df_drawdown.loc[date_mdd]          
    period_mdd = len(slice_timeseries_by_dates(timeseries=df_drawdown, start_date=row_mdd['date_peak'], end_date=date_mdd))
    dct_mdd = {
        'name': name,
        'mdd': row_mdd['drawdown'],
        'date_peak': row_mdd['date_peak'],
        'date_trough': date_mdd,
        'peak': row_mdd['historical_peak'],
        'trough': row_mdd['trough'],
        'period_mdd': period_mdd,
    }
    return dct_mdd

def map_single_cumreturns_to_data_maxdrawdown(cumreturns: pd.DataFrame)-> dict:
    return pipe(
        map_single_cumreturns_to_df_drawdown,
        map_df_drawdown_to_data_maxdrawdown
    )(cumreturns)

def map_single_prices_to_data_maxdrawdown(prices: pd.DataFrame)-> pd.DataFrame:
    return pipe(
        map_prices_to_cumreturns,
        map_single_cumreturns_to_data_maxdrawdown
    )(prices)

get_data_maxdrawdown = map_single_prices_to_data_maxdrawdown
calculate_maxdrawdown = lambda prices: getitem(get_data_maxdrawdown(prices), 'mdd')

def map_prices_to_data_maxdrawdowns(prices: pd.DataFrame)-> list[pd.DataFrame]:
    map_prices_to_single_cumreturns = pipe(
        map_prices_to_cumreturns,
        map_timeseries_to_single_timeserieses,
    )
    return list(map(map_single_cumreturns_to_data_maxdrawdown, map_prices_to_single_cumreturns(prices)))

map_prices_to_maxdrawdowns = lambda prices: dict(map(lambda data: (data['name'], data['mdd']), map_prices_to_data_maxdrawdowns(prices)))

get_data_maxdrawdowns = map_prices_to_data_maxdrawdowns
calculate_maxdrawdowns = map_prices_to_maxdrawdowns