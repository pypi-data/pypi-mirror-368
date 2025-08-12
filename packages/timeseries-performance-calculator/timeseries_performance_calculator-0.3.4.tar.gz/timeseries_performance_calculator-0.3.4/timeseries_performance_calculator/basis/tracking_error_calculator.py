from .basis import validate_returns_with_benchmark

def calculate_tracking_error(returns):
    validate_returns_with_benchmark(returns)
    excess_return = returns.iloc[:, 0] - returns.iloc[:, 1] 
    tracking_error = excess_return.std()
    return tracking_error