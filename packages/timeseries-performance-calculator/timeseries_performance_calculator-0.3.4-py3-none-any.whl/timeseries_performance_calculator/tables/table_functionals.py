import pandas as pd
from universal_timeseries_transformer import PricesMatrix
from timeseries_performance_calculator.basis import calculate_return

def map_prices_to_table_iterated_returns(prices: pd.DataFrame, option_iterated: str = 'monthly') -> pd.DataFrame:
    pm = PricesMatrix(prices)

    def create_table(label, date_pair):
        columns = pm.rows_by_names((date_pair[0], date_pair[1])).T
        returns = calculate_return(columns.iloc[:, 0], columns.iloc[:, -1])
        return returns.to_frame(label)
    
    mapping_date_pairs = {
        'monthly': pm.monthly_date_pairs,
        'yearly': pm.yearly_date_pairs,
        'period': pm.historical_date_pairs,
    }
    date_pairs = mapping_date_pairs[option_iterated]

    tables = [create_table(label, date_pair) 
              for label, date_pair in date_pairs.items()]
    return pd.concat(tables, axis=1)