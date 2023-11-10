#sample: ema base strategy using import from binance data
# library imports
import sys
import src.strategies.sources as sources
import src.utilities.get_data.binance_data as binance_data
import pandas_ta as ta
import src.indicators.i_ema as indicator
import src.utilities.noshare_data as noshare_data
from backtesting import Backtest, Strategy
from backtesting.lib import resample_apply
from os import listdir
from os.path import isfile, join
from pathlib import Path  

# define strategy
class ema_strategy(Strategy):
    #base ema backtested
    fast_ema_period = 7
    slow_ema_period = 18

    def init(self):
        #calculate ema dataframes
        self.fast_ema_indicator = self.I(indicator.i_ema, self.data, ema_period = self.fast_ema_period, overlay=True)
        self.slow_ema_indicator = self.I(indicator.i_ema, self.data, ema_period = self.slow_ema_period, overlay=True)
     
    def next(self):
        #get step to step ema data
        fast_ema = self.fast_ema_indicator[-1]
        slow_ema = self.slow_ema_indicator[-1]
        #defining how to open/close position
        if self.position:
             if fast_ema < slow_ema:
                self.position.close()
        else:
             if (
                fast_ema > slow_ema
                ):
                self.buy()

#retrive data / use tradinview_data in utilities if data come from tradingview
path = sys.path[noshare_data.project_sys_path_position] + "\\data"
timeframe = "in_sample"
filename = "AAVEUSDT.csv"
data = binance_data.read_csv_data(path, timeframe, filename)

#launching backtested
bt = Backtest(data[data.index > "2017-01-01"], ema_strategy, cash=sources.cash,  commission=sources.commission)
stats = bt.optimize(
        fast_ema_period = range(8, 12, 1),
        slow_ema_period = range(12, 14, 1),
        constraint= lambda param: param.slow_ema_period > param.fast_ema_period,
        maximize="Equity Final [$]"
    )
#plot backtest result
bt.plot(resample=False)