from functools import cached_property
import pandas as pd
from universal_timeseries_transformer import (
    PricesMatrix, 
    decompose_timeserieses_to_list_of_timeserieses, 
    plot_timeseries, 
    transform_timeseries, 
    extend_timeseries_by_all_dates,
    )
from timeseries_performance_calculator.tables.total import get_dfs_tables_year
from timeseries_performance_calculator.cross_sectional_analysis import (
    get_crosssectional_total_performance, 
    get_crosssectional_total_performance_without_benchmark, 
    get_crosssectional_period_returns,
    get_crosssectional_yearly_returns,
    get_crosssectional_monthly_returns,
    get_crosssectional_yearly_relative,
    get_crosssectional_annualized_return_cagr,
    get_crosssectional_annualized_return_days,
    get_crosssectional_annualized_volatility,
    get_crosssectional_maxdrawdown,
    get_crosssectional_sharpe_ratio,
    get_crosssectional_beta,
    get_crosssectional_winning_ratio,
)
from timeseries_performance_calculator.cross_sectional_analysis.parser import get_benchmark_price_in_prices, get_component_prices_in_prices
from .basis import get_table_seasonality


class Performance:
    def __init__(self, timeseries, benchmark_index: int = None, benchmark_name: str = None, benchmark_timeseries: pd.DataFrame = None, free_returns: pd.DataFrame = None):
        self.set_benchmark_and_components(timeseries, benchmark_index, benchmark_name, benchmark_timeseries)
        self.free_returns = free_returns

    def set_benchmark_and_components(self, timeseries, benchmark_index: int = -1, benchmark_name: str = None, benchmark_timeseries: pd.DataFrame = None) -> pd.DataFrame:

        def transform_timeseries_canonically(timeseries):
            return transform_timeseries(extend_timeseries_by_all_dates(timeseries), option_type='str')
        self.timeseries = transform_timeseries_canonically(timeseries)

        if benchmark_timeseries is not None:
            if benchmark_timeseries.columns[0] in self.timeseries.columns:
                self.benchmark_name = benchmark_name
                self.benchmark_index = self.timeseries.columns.get_loc(self.benchmark_name)
                self.component_timeserieses = get_component_prices_in_prices(self.timeseries, benchmark_index=self.benchmark_index)
                self.benchmark_timeseries = get_benchmark_price_in_prices(self.timeseries, benchmark_index=self.benchmark_index)
                self.ordered_timeserieses = pd.concat([*self.component_timeserieses, self.benchmark_timeseries], axis=1).ffill()
            else:
                self.component_timeserieses = decompose_timeserieses_to_list_of_timeserieses(self.timeseries)
                self.ordered_timeserieses = pd.concat(self.component_timeserieses, axis=1).join(benchmark_timeseries).ffill()
                self.benchmark_name = benchmark_timeseries.columns[0]
                self.benchmark_index = self.ordered_timeserieses.columns.get_loc(self.benchmark_name)
                self.benchmark_timeseries = self.ordered_timeserieses[[self.benchmark_name]]
        else:   
            if benchmark_name is not None:
                self.benchmark_timeseries = get_benchmark_price_in_prices(self.timeseries, benchmark_name=benchmark_name)
                self.benchmark_name = benchmark_name
                self.benchmark_index = self.timeseries.columns.get_loc(self.benchmark_name)
                self.component_timeserieses = get_component_prices_in_prices(self.timeseries, benchmark_index=self.benchmark_index)
                self.ordered_timeserieses = pd.concat([*self.component_timeserieses, self.benchmark_timeseries], axis=1).ffill()
            elif benchmark_index is not None:
                self.benchmark_timeseries = get_benchmark_price_in_prices(self.timeseries, benchmark_index=benchmark_index)
                self.benchmark_name = self.benchmark_timeseries.columns[0]
                self.benchmark_index = self.timeseries.columns.get_loc(self.benchmark_name)
                self.component_timeserieses = get_component_prices_in_prices(self.timeseries, benchmark_index=self.benchmark_index)
                self.ordered_timeserieses = pd.concat([*self.component_timeserieses, self.benchmark_timeseries], axis=1).ffill()
            else:
                self.benchmark_name = None
                self.benchmark_index = None
                self.benchmark_timeseries = None
                self.component_timeserieses = decompose_timeserieses_to_list_of_timeserieses(self.timeseries)
                self.ordered_timeserieses = pd.concat([*self.component_timeserieses], axis=1).ffill()
        
    @cached_property
    def pm(self):
        return PricesMatrix(self.ordered_timeserieses)
    
    @cached_property
    def prices(self):
        return self.pm.df

    @cached_property
    def pms(self):
        lst_of_prices = decompose_timeserieses_to_list_of_timeserieses(self.ordered_timeserieses)
        return [PricesMatrix(df) for df in lst_of_prices]

    @cached_property
    def returns(self):
        lst_of_returns = [pm.returns for pm in self.pms]
        return pd.concat(lst_of_returns, axis=1)
    
    @cached_property
    def cumreturns(self):
        lst_of_cumreturns = [pm.cumreturns for pm in self.pms]
        return pd.concat(lst_of_cumreturns, axis=1)
    
    @cached_property
    def total_performance(self):
        if self.benchmark_timeseries is not None:
            return get_crosssectional_total_performance(self.ordered_timeserieses, free_returns=self.free_returns)
        else:
            return get_crosssectional_total_performance_without_benchmark(self.ordered_timeserieses, free_returns=self.free_returns)
    
    @cached_property
    def period_returns(self):
        return get_crosssectional_period_returns(self.ordered_timeserieses)
    
    @cached_property
    def yearly_returns(self):
        return get_crosssectional_yearly_returns(self.ordered_timeserieses)
    
    @cached_property
    def monthly_returns(self):
        return get_crosssectional_monthly_returns(self.ordered_timeserieses)
    
    @cached_property
    def yearly_relative(self):
        return get_crosssectional_yearly_relative(self.ordered_timeserieses)
    
    @cached_property
    def annualized_return_cagr(self):
        return get_crosssectional_annualized_return_cagr(self.ordered_timeserieses)
    
    @cached_property
    def annualized_return_days(self):
        return get_crosssectional_annualized_return_days(self.ordered_timeserieses)
    
    @cached_property
    def annualized_volatility(self):
        return get_crosssectional_annualized_volatility(self.ordered_timeserieses)
    
    @cached_property
    def maxdrawdown(self):
        return get_crosssectional_maxdrawdown(self.ordered_timeserieses)
    
    @cached_property
    def sharpe_ratio(self):
        return get_crosssectional_sharpe_ratio(self.ordered_timeserieses, free_returns=self.free_returns)
    
    @cached_property
    def beta(self):
        if self.benchmark_timeseries is not None:
            return get_crosssectional_beta(self.ordered_timeserieses)
        else:
            raise ValueError("Benchmark timeseries is required to calculate beta")
    
    @cached_property
    def winning_ratio(self):
        if self.benchmark_timeseries is not None:
            return get_crosssectional_winning_ratio(self.ordered_timeserieses)
        else:
            raise ValueError("Benchmark timeseries is required to calculate winning ratio")
        
    def plot_cumreturns(
            self, 
            title=None, 
            option_last_name=False, 
            option_last_value=True, 
            option_main=False, 
            option_num_to_show=None,
            figsize=None
            ):
        return plot_timeseries(
            self.cumreturns.fillna(0), 
            title=title if title is not None else f"Cumreturns: {list(self.ordered_timeserieses.columns[:5])}",
            option_last_name=option_last_name, 
            option_last_value=option_last_value, 
            option_main=option_main, 
            option_num_to_show=option_num_to_show if option_num_to_show is not None else len(self.cumreturns.columns),
            figsize=figsize if figsize is not None else (10, 5)
            );

    def get_seasonality(self, index_name):
        return get_table_seasonality(self.monthly_returns, index_name)
    
    def get_relative_seasonality(self, index_name):
        df_port = get_table_seasonality(self.monthly_returns, index_name)
        df_bm = get_table_seasonality(self.monthly_returns, self.benchmark_name)
        df_relative = df_port - df_bm
        df_relative = df_relative.dropna(axis=0, how='all')
        return df_relative
