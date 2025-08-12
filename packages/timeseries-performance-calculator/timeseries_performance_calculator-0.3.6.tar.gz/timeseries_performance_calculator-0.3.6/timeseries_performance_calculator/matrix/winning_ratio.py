import pandas as pd
from functools import partial
from itertools import permutations
from timeseries_performance_calculator.functionals import pipe
from timeseries_performance_calculator.basis.winning_ratio_calculator import calculate_winning_ratio

def create_frame_of_square_matrix(df: pd.DataFrame, option_column: bool = True)-> pd.DataFrame:
    basis = df.columns if option_column else df.index
    return pd.DataFrame(index=basis, columns=basis)
    
def fill_cell_on_square_matrix(prices: pd.DataFrame, matrix:pd.DataFrame)-> pd.DataFrame:
    for idx, col in list(permutations(matrix.index, 2)):
        pair = [idx, col]
        cell = calculate_winning_ratio(prices[pair]) if idx != col else np.nan
        matrix.loc[idx, col] = cell
    return matrix

def get_label_coordinates(matrix:pd.DataFrame, i: int, j: int) -> tuple:
    return [matrix.index[i], matrix.columns[j]]

def get_matrix_of_winning_ratio(prices: pd.DataFrame)-> pd.DataFrame:
    return pipe(
        create_frame_of_square_matrix,
        partial(fill_cell_on_square_matrix, prices)
    )(prices)