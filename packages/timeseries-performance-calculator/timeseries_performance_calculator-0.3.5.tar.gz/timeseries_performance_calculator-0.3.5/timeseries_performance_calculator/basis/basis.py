import pandas as pd

def validate_returns_with_benchmark(returns: pd.DataFrame) -> None:
    if returns.shape[1] != 2:
        raise ValueError("DataFrame must have exactly 2 columns")
