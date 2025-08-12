from timeseries_performance_calculator.tables.monthly_relative_table import map_prices_to_table_monthly_relative

def validate_prices_for_winning_ratio(prices):
    if prices.shape[1] != 2:
        raise ValueError("DataFrame must have exactly 2 columns")

def calculate_winning_ratio(prices):
    validate_prices_for_winning_ratio(prices)
    df = map_prices_to_table_monthly_relative(prices)
    return df.T['relative'].map(lambda x: x>=0).mean()
