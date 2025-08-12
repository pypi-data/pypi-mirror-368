from functools import reduce
from functools import cached_property
from universal_timeseries_transformer import extend_timeseries_by_all_dates, transform_timeseries
from .performance import Performance

class Seasonality:
    def __init__(self, timeseries, benchmark_timeseries=None):
        self.timeseries = timeseries
        self.benchmark_timeseries = benchmark_timeseries if benchmark_timeseries is not None else self.set_null_timeseries()
        self.perf = Performance(timeseries=self.timeseries, benchmark_timeseries=self.benchmark_timeseries)
        self.index_name = self.timeseries.columns[0]
        self.benchmark_name = self.benchmark_timeseries.columns[0]

    def set_null_timeseries(self):
        null_timeseries = self.timeseries.rename(columns={self.timeseries.columns[0]: 'null'})
        null_timeseries.iloc[:, 0] = 0
        return null_timeseries

    @cached_property
    def prices(self):
        timeseries_extended = extend_timeseries_by_all_dates(transform_timeseries(self.timeseries, option_type='str'))
        lst_of_prices = [timeseries_extended, self.benchmark_timeseries]
        prices = reduce(lambda x, y: x.join(y, how='left'), lst_of_prices)
        prices = prices.ffill()
        return prices

    @cached_property
    def seasonality(self):
        return self.perf.get_seasonality(self.index_name)
    
    @cached_property
    def benchmark_seasonality(self):
        return self.perf.get_seasonality(self.benchmark_name)
    
    @cached_property
    def relative_seasonality(self):
        return self.perf.get_relative_seasonality(self.index_name)
    

# class Seasonality:
#     def __init__(self, ticker, benchmark_ticker):
#         self.ticker = ticker
#         self.benchmark_ticker = benchmark_ticker
#         self.timeseries = get_timeseries_price(ticker)
#         self.benchmark_timeseries = get_timeseries_price(benchmark_ticker)
#         self.loader = SeasonalityLoader(ticker, benchmark_ticker)

#     def get_seasonality(self, index_name):
#         return self.loader.perf.get_seasonality(index_name)
    
#     def get_relative_seasonality(self, index_name):
#         return self.loader.perf.get_relative_seasonality(index_name)