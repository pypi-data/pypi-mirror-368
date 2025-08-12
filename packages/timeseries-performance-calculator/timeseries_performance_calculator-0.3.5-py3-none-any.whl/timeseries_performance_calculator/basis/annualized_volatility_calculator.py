import numpy as np
import pandas as pd

DEFAULT_ANNUAL_TRADING_DAYS = 252

def calculate_annualized_volatility(returns: pd.DataFrame, annual_trading_days: int = DEFAULT_ANNUAL_TRADING_DAYS) -> pd.DataFrame:
    std = returns.std()
    annualized_volatility = std * np.sqrt(annual_trading_days)
    return annualized_volatility