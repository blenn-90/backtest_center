#%% libraries
from sources import * 
import sys
import src.utilities.import_data as import_data
from backtesting import Backtest, Strategy
from backtesting.lib import resample_apply
import pandas_ta as ta
from os import listdir
from os.path import isfile, join
from pathlib import Path  


#%% indicator
def ema(data, length):
    ema =  ta.ema(close = data.Close.s, length = length)
    return ema.to_numpy().T

#%% define strategy
class ema_strategy(Strategy):
    number_of_candle_to_msb = 4
    fast_ema_period = 7
    slow_ema_period = 18
    expansion_bar_length = 55
    atr_multiply = 1.5

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
timeframe = "binance_1d"
filename = "ETHUSDT.csv"
data = import_data.tradingview_csv_to_dataframe(path, timeframe, filename)
#print("-->launching backtest")
bt = Backtest(data[data.index > "2019-01-01"], ema_strategy, cash=cash,  commission=commission)
stats = bt.optimize(
        fast_ema_period = range(8, 12, 1),
        slow_ema_period = range(12, 14, 1),
        constraint= lambda param: param.slow_ema_period > param.fast_ema_period,
        maximize="Equity Final [$]"
    )
print(stats)