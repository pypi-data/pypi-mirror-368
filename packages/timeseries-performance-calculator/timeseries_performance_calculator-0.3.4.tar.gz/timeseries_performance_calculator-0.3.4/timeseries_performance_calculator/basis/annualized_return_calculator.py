import pandas as pd

def calculate_annualized_return_cagr(cumreturns: pd.Series, trading_days: int)-> pd.Series:
    annualized_return_cagr = ((1+cumreturns/100)**(365/trading_days)-1)*100
    return annualized_return_cagr    

def calculate_annualized_return_days(cumreturns: pd.Series, trading_days: int)-> pd.Series:
    number_of_days = trading_days-1
    annualized_return_days = cumreturns/number_of_days*365
    return annualized_return_days

# def calculate_annualized_return_cagr(cumreturn: float, trading_days: int)-> float:
#     annualized_return_cagr = ((1+cumreturn/100)**(365/trading_days)-1)*100
#     return annualized_return_cagr    

# def calculate_annualized_return_days(cumreturn: float, trading_days: int)-> float:
#     number_of_days = trading_days-1
#     annualized_return_days = cumreturn/number_of_days*365
#     return annualized_return_days
