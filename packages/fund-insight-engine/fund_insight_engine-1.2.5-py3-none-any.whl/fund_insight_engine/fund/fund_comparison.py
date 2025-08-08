from functools import cached_property
from universal_timeseries_transformer import slice_timeseries_by_dates
from universal_timeseries_transformer.matrix_representation.prices_matrix import PricesMatrix
from fund_insight_engine.price_retriever.utils import get_timeserieses_price
from timeseries_performance_calculator.performance import Performance

class FundComparison:
    def __init__(self, tickers: list[str], start_date: str=None, end_date: str=None, index_ref: str=None):
        self.tickers = tickers
        self.ticker = self.set_ticker()
        self.benchmark = self.set_benchmark()
        self.start_date = start_date
        self.end_date = end_date
        self.index_ref = index_ref

    def set_ticker(self):
        return self.tickers[0]
    
    def set_benchmark(self):
        return self.tickers[1]

    @cached_property
    def corrected_prices(self):
        corrected_prices = get_timeserieses_price(self.tickers)
        return slice_timeseries_by_dates(corrected_prices, self.start_date, self.end_date)

    @cached_property
    def list_of_corrected_prices(self):
        return [self.corrected_prices[[col]] for col in self.corrected_prices.columns]

    @cached_property
    def p(self):
        return Performance(self.corrected_prices)
    
    @cached_property
    def returns(self):
        return self.p.returns
    
    @cached_property
    def cumreturns(self):
        return self.p.cumreturns

    @cached_property
    def prices(self):
        return self.corrected_prices.iloc[1:, :]

    @cached_property
    def total_performance(self):
        return self.p.total_performance
    
    @cached_property
    def period_returns(self):
        return self.p.period_returns

    @cached_property
    def yearly_returns(self):
        return self.p.yearly_returns
    
    @cached_property
    def monthly_returns(self):
        return self.p.monthly_returns
    
    @cached_property
    def dfs_tables_year(self):
        return self.p.dfs_tables_year
    