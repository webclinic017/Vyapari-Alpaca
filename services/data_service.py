import logging
import time
from enum import Enum
from typing import List

from fmp_python.fmp import FMP, Interval
from kink import inject
from pandas import DataFrame, concat


class Timeframe(Enum):
    MIN_1 = "1Min"
    MIN_5 = "5Min"
    MIN_15 = "15Min"
    DAY = 'day'


@inject
class DataService(object):

    def __init__(self):
        self.api = FMP()

        # Initialize a logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_current_price(self, symbol) -> float:
        return self.api.get_quote_short(symbol).iloc[-1]['price']

    '''
    Returns dataframe in ascending order
    '''
    def get_daily_bars(self, symbol: str, limit: int) -> DataFrame:
        bars = self.api.get_historical_price(symbol, limit)[::-1]
        bars.set_index('date', inplace=True)
        return bars

    def get_intra_day_bars(self, symbol: str, interval: Interval):
        bars = self.api.get_historical_chart(symbol, interval)[::-1]
        bars.set_index('date', inplace=True)
        return bars

    '''
    Dataframe response:
      symbol      1D       5D  ...          5Y          10Y           max
    0   AAPL -0.7004  0.04213  ...   335.21191    915.88235  147909.34944
    1   NVDA -1.9295 -3.11486  ...  1148.71929  12213.40206  116381.37312
    '''
    def stock_price_change(self, symbols: List[str]) -> DataFrame:
        retry_count = 5
        dfs = []

        for sym in symbols:
            result = None
            for attempt in range(1, retry_count + 1):
                result = self.api.stock_price_change(sym)
                if isinstance(result, DataFrame) and not result.empty:
                    self.logger.info(result)
                    dfs.append(result)
                    break  # Break out of the retry loop if result is not None
                else:
                    self.logger.warning(
                        f"Attempt {attempt}/{retry_count} for {sym} returned None. Retrying..."
                    )
                    # Add a delay between retries
                    time.sleep(1)  # 1-second delay

            if isinstance(result, DataFrame) and result.empty:
                self.logger.warning(f"API call for {sym} returned None after {retry_count} attempts.")

        return concat(dfs, ignore_index=True)

    def save_history(self, symbol, interval: Interval, limit: int = 252):
        pass

    def screen_stocks(self, market_cap_lt: int = None, market_cap_gt: int = None, price_lt: int = None,
                      price_gt: int = None, beta_lt: float = None, beta_gt: float = None, volume_lt: int = None,
                      volume_gt: int = None, is_etf: bool = None, limit: int = 1000) -> DataFrame:
        # (volume_gt=100000, price_gt=20, price_lt=500, beta_gt=0.3, limit=5000)
        return self.api.get_stock_screener(market_cap_lt=market_cap_lt, market_cap_gt=market_cap_gt,
                                           volume_lt=volume_lt, volume_gt=volume_gt, price_lt=price_lt,
                                           price_gt=price_gt, is_etf=is_etf, beta_lt=beta_lt,
                                           beta_gt=beta_gt, exchange=['NYSE', 'NASDAQ', 'AMEX'], limit=limit)
