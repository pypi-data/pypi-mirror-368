from itertools import starmap
from universal_timeseries_transformer import PricesMatrix
from timeseries_performance_calculator.dataframe_basis.dataframe_calculator import get_cumreturns_row_between_dates
import pandas as pd

def get_yearly_cumreturns_table(prices: pd.DataFrame) -> pd.DataFrame:
    pm = PricesMatrix(prices)
    def extract_all_combinations(dct):
        return [
            (year, date_pair)
            for year, date_pair in dct.items()
        ]
    
    def create_dataframe(year, date_pair):
        return get_cumreturns_row_between_dates(
            pm.df,
            date_i=date_pair[0],
            date_f=date_pair[1],
            label_cumreturn=f'{year}'
        )

    data_yearly_date_pairs = pm.ytd_date_pairs
    
    combinations = extract_all_combinations(data_yearly_date_pairs)
    dfs = starmap(create_dataframe, combinations)
    return pd.concat(dfs, axis=0)
