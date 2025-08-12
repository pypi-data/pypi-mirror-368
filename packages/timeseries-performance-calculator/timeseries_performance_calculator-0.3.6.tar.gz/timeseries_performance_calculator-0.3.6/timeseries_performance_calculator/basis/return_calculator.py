from typing import Union
import pandas as pd

def calculate_return(start: Union[float, pd.Series], end: Union[float, pd.Series]) -> Union[float, pd.Series]:
    return (end / start - 1) * 100
