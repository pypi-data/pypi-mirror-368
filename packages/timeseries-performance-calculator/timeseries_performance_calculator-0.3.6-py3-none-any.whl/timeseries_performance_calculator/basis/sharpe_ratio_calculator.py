import pandas as pd
import numpy as np
from universal_timeseries_transformer import extend_timeseries_by_all_dates
from aws_s3_controller import load_csv_in_bucket
from .basis import validate_returns_with_free_returns

def calculate_sharpe_ratio(returns, free_returns=None):
    if free_returns is None:
        free_returns = pd.DataFrame(data={'date': returns.index, 'zero_free_return': 0}).set_index('date')
    returns_with_free = returns.join(extend_timeseries_by_all_dates(free_returns), how='left').ffill()
    validate_returns_with_free_returns(returns_with_free)
    expected_return = returns_with_free.iloc[:, 0].mean() 
    std = returns_with_free.iloc[:, 0].std()
    expected_free_return = returns_with_free.iloc[:, 1].mean()
    ANNUAL_DAYS = 365
    annualized_expected_fund_return = expected_return*ANNUAL_DAYS
    annualized_expected_free_return = expected_free_return*ANNUAL_DAYS
    annualized_expected_excess_return = annualized_expected_fund_return - annualized_expected_free_return
    annualized_fund_std = std * np.sqrt(ANNUAL_DAYS)
    sharpe_ratio = annualized_expected_excess_return / annualized_fund_std
    return sharpe_ratio

# temp: import from aws_s3
def load_free_returns_from_s3():
    menu5105 = load_csv_in_bucket(bucket='dataset-system', bucket_prefix='dataset-menu5105', regex='menu5105-code000005')
    COLS_TO_KEEP = ['구간초일', 'Rf']
    MAPPING_COLUMNS = {'구간초일': 'date', 'Rf': 'GVSK1YR'}
    df = (
        menu5105[COLS_TO_KEEP]
        .rename(columns=MAPPING_COLUMNS)
        .set_index('date')
    )
    return df