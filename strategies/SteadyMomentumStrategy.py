import time
from typing import Dict
from kink import di
from pandas import DataFrame
from sklearn.linear_model import LinearRegression
import numpy as np

from core.logger import logger
from core.schedule import SafeScheduler, JobRunType
from services.notification_service import Notification
from universe.watchlist import WatchList
from services.account_service import AccountService
from services.data_service import DataService
from services.order_service import OrderService
from services.position_service import PositionService, Position
from strategies.strategy import Strategy
from tabulate import tabulate

'''
    Step 1: Get a list of popular stocks/ETFs
    Step 2: Run the steady momentum strategy: 
    -   The strategy identifies stocks in a steady uptrend by analyzing their slope and percentage of up days, 
        then ranks them based on how often they fall below the 30-day EMA and the strength of their uptrend. 
        The top 50 stocks with the fewest drops below the EMA and the highest slope are selected.
    Step 3: Select the top 30 for investing
    Step 4: Replace a stock only if it does not exist in the top 50 stocks

    Inspired from: the MomentumStrategy
    
'''

MAX_STOCKS_TO_PURCHASE = 30


class SteadyMomentumStrategy(Strategy):

    def __init__(self):
        self.watchlist = WatchList()
        self.order_service: OrderService = di[OrderService]
        self.position_service: PositionService = di[PositionService]
        self.data_service: DataService = di[DataService]
        self.account_service: AccountService = di[AccountService]
        self.schedule: SafeScheduler = di[SafeScheduler]
        self.notification: Notification = di[Notification]

        self.stock_picks_today: DataFrame = DataFrame()
        self.stocks_traded_today: list[str] = []

    def get_algo_name(self) -> str:
        return type(self).__name__

    def get_universe(self) -> None:
        pass

    def download_data(self, symbols: list[str], start_date: str, end_date: str) -> DataFrame:
        pass

    def define_buy_sell(self, data):
        pass

    def init_data(self) -> None:
        self.stock_picks_today: DataFrame = self.prep_stocks()
        tabled_stock_picks = tabulate(self.stock_picks_today, headers='keys', tablefmt='pretty')
        logger.info(f"Stock picks for today:\n{tabled_stock_picks}")
        self._run_trading()

    # ''' Since this is a strict LONG TERM strategy, run it every 24 hrs '''
    def run(self, sleep_next_x_seconds, until_time):
        self.schedule.run_adhoc(self.run_dummy, sleep_next_x_seconds, until_time, JobRunType.STANDARD)

    def prep_stocks(self) -> DataFrame:
        logger.info("Downloading data ...")

        # Get universe from the watchlist
        from_watchlist: list[str] = self.watchlist.get_universe(1000000, 0.6, price_gt=10)
        from_positions: list[str] = [pos.symbol for pos in self.position_service.get_all_positions()]
        universe: list[str] = sorted(list(set(from_watchlist + from_positions)))

        # Fetch stock price change data
        hqm_base: DataFrame = self.data_service.stock_price_change(universe)

        # Filter out the stocks that don't meet the below criteria
        hqm = hqm_base[
            (hqm_base['6M'] > hqm_base['3M']) &  # '6M' change is greater than '3M'
            (hqm_base['3M'] >= 10)  # '3M' change is at least 10%
            ]

        # Calculate if the stock has steady momentum
        return self._calculate_stock_momentum(hqm)

    def _calculate_stock_momentum(self, hqm: DataFrame) -> DataFrame:
        results = []
        thresholds = [0.8, 0.7, 0.6, 0.5]  # Percentage of up days

        for symbol in hqm['symbol']:
            # Fetch daily OHLCV data
            data = self.data_service.get_daily_bars(symbol, 100)

            # Step 2: Calculate Exponential Moving Average (EMA)
            data['EMA_30'] = data['close'].ewm(span=30, adjust=False).mean()

            # Step 3: Calculate the slope using linear regression
            recent_data = data[-45:]
            x = np.array(range(len(recent_data))).reshape(-1, 1)
            y = recent_data['close'].values

            # Fit linear regression
            model = LinearRegression()
            model.fit(x, y)
            slope = model.coef_[0]

            # Step 4: Check the slope and steadiness
            is_steady_uptrend = slope > 0
            up_days = np.sum(recent_data['close'].diff() > 0)
            steady_percent = up_days / len(recent_data)

            # Calculate the count of days the stock has fallen below the 30-day EMA
            below_ema_count = np.sum(recent_data['close'] < recent_data['EMA_30'])

            # Print the rows where the closing price is below the 30-day EMA
            below_ema_df = recent_data[recent_data['close'] < recent_data['EMA_30']]
            print(below_ema_df)

            # Determine which threshold the stock meets
            threshold_met = None
            for threshold in thresholds:
                if steady_percent >= threshold:
                    threshold_met = threshold
                    break

            # Store the results
            results.append({
                'Symbol': symbol,
                'Slope': slope,
                'Steady Uptrend': is_steady_uptrend,
                'Steady': steady_percent,
                'Steady Threshold Met': threshold_met,
                'Below EMA Count': below_ema_count
            })

        # Convert the results to a DataFrame
        results_df = DataFrame(results)

        # Filter the symbols that have a steady uptrend and meet any of the thresholds
        filtered_results = results_df[
                (results_df['Steady Uptrend']) &
                (results_df['Steady Threshold Met'].notnull())
            ]

        # Sort by 'Below EMA Count' in ascending order, then by 'Slope' in descending order
        filtered_results = filtered_results.sort_values(
            by=['Below EMA Count', 'Slope'],
            ascending=[True, False]
        )

        # Add a 'Rank' column based on the order after sorting
        filtered_results['Rank'] = filtered_results['Below EMA Count'].rank(method='first', ascending=True)

        # Return the top 50 stocks according to the strategy
        buffer: int = 20
        return filtered_results.head(MAX_STOCKS_TO_PURCHASE + buffer)

    def _run_trading(self):
        if not self.order_service.is_market_open():
            logger.warning("Market is not open!")
            return

        held_stocks: Dict[str, Position] = {pos.symbol: pos for pos in self.position_service.get_all_positions()}
        top_picks_today = self.stock_picks_today['Symbol'].unique()

        # Identify stocks to be sold
        to_be_removed = [held_stock for held_stock in held_stocks if held_stock not in top_picks_today]

        if to_be_removed:
            # Liquidate the selected stocks
            for stock in to_be_removed:
                self.notify_to_liquidate(held_stocks[stock])
                self.order_service.market_sell(stock, int(held_stocks[stock].qty))
                del held_stocks[stock]

            time.sleep(10)  # Allow sufficient time for the stocks to liquidate
            logger.info("Above stocks have been liquidated")
        else:
            logger.info("No stocks to be liquidated today")

        account = self.account_service.get_account_details()
        logger.info(f"Current Balance: ${account.buying_power}")

        buffer: int = 10
        top_picks_addn = top_picks_today[:MAX_STOCKS_TO_PURCHASE + buffer]
        top_picks_final = [stock for stock in top_picks_addn if stock not in held_stocks]
        self.rebalance_stocks(top_picks_final)

    def rebalance_stocks(self, symbols: list[str]):
        account = self.account_service.get_account_details()
        allocated_amt_per_symbol = float(account.portfolio_value) / MAX_STOCKS_TO_PURCHASE

        held_stocks = {pos.symbol: int(pos.qty) for pos in self.position_service.get_all_positions()}
        position_count = 0

        def calculate_qty_and_buy(sym: str) -> None:
            nonlocal position_count
            if position_count >= MAX_STOCKS_TO_PURCHASE:
                return

            current_price = self.data_service.get_current_price(sym)
            qty = int(allocated_amt_per_symbol / current_price)
            current_qty = held_stocks.get(sym, 0)
            qty_to_add = qty - current_qty

            if qty_to_add > 0:
                self.order_service.market_buy(sym, int(qty_to_add))
                position_count += 1
                held_stocks[sym] = current_qty + qty_to_add
                time.sleep(3)  # Allow sufficient time to purchase

        # Re-balance held stocks
        for symbol in held_stocks:
            logger.info(f"Balancing for HELD symbol: {symbol}")
            calculate_qty_and_buy(symbol)

        # Re-balance selected symbols
        for symbol in set(symbols):
            if symbol not in held_stocks:
                logger.info(f"Balancing for NEW symbol: {symbol}")
                calculate_qty_and_buy(symbol)

        logger.info("All stocks rebalanced for today")

    def notify_to_liquidate(self, position: Position):
        msg = f"Selling {position.qty} of {position.symbol} at a total ${float(position.market_value):.2f}\n"
        if float(position.unrealized_pl) > 0:
            msg += f"at a PROFIT of {float(position.unrealized_pl):.2f} ({float(position.unrealized_plpc):.2f}%)"
        else:
            msg += f"at a LOSS of {float(position.unrealized_pl):.2f} ({float(position.unrealized_plpc):.2f}%)"
        self.notification.notify(msg)

    @staticmethod
    def run_dummy():
        logger.info("Running dummy job ...")
