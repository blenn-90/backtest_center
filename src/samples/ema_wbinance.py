#%% libraries
import sys
import src.samples.sources as sources
import src.utilities.binance_data as binance_data
import pandas_ta as ta
from backtesting import Backtest, Strategy
from backtesting.lib import resample_apply
from os import listdir
from os.path import isfile, join
from pathlib import Path  


#%% indicator
def ema(data, length):
    ema =  ta.ema(close = data.Close.s, length = length)
    return ema.to_numpy().T

#%% define strategy
class ema_strategy(Strategy):
    fast_ema_period = 7
    slow_ema_period = 18

    def init(self):
        self.fast_ema_indicator = self.I(ema, self.data, length = self.fast_ema_period, overlay=True)
        self.slow_ema_indicator = self.I(ema, self.data, length = self.slow_ema_period, overlay=True)

    def next(self):
        fast_ema = self.fast_ema_indicator[-1]
        slow_ema = self.slow_ema_indicator[-1]

        if self.position:
             if fast_ema < slow_ema:
                self.position.close()
        else:
             if (
                fast_ema > slow_ema
                ):
                self.buy()

#retrive data
path = sys.path[1] + "\\data"
timeframe = "binance_4h"
filename = "ETHUSDT.csv"
data = binance_data.read_csv_data(path, timeframe, filename)
#print("-->launching backtest")
bt = Backtest(data[data.index > "2017-01-01"], ema_strategy, cash=sources.cash,  commission=sources.commission)
stats = bt.optimize(
        fast_ema_period = range(8, 12, 1),
        slow_ema_period = range(12, 14, 1),
        constraint= lambda param: param.slow_ema_period > param.fast_ema_period,
        maximize="Equity Final [$]"
    )
bt.plot(resample=False)