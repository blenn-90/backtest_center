import numpy as np 
from pandas import DataFrame
import matplotlib.pyplot as plt

index = range(20, 28, 2)
columns = range(60, 64, 1)
df = DataFrame(np.array([[2, 13, 44, 5], [2, 53, 4, 58],[2, 33, 54, 5],[2, 34, 4, 55]]), index=index, columns=columns)
print(df)
plt.pcolor(df)
plt.yticks(np.arange(0.5, len(df.index), 1), df.index)
plt.xticks(np.arange(0.5, len(df.columns), 1), df.columns)
plt.show()#sample: ema base strategy using import from binance data
# library imports
import sys
import src.strategies.sources as sources
import src.utilities.get_data.binance_data as binance_data
import src.strategies.strategy_ema.str_ema_cross_w_hardstop as strategy
import pandas_ta as ta
import pandas as pd
import src.indicators.i_ema as indicator
import src.utilities.noshare_data as noshare_data
from backtesting import Backtest, Strategy
from backtesting.lib import resample_apply
from os import listdir
from os.path import isfile, join
from pathlib import Path  
import seaborn as sns
import matplotlib.pyplot as plt

#retrive data / use tradinview_data in utilities if data come from tradingview
path = sys.path[noshare_data.project_sys_path_position] + "\\data"
timeframe = "binance_4h"
filename = "BTCUSDT.csv"
data = binance_data.read_csv_data(path, timeframe, filename)
print(data)
#launching backtested
bt = Backtest(data[ (data.index > "2021-01-01") & (data.index < "2022-01-01")], strategy.ema_cross_w_hardstop_strategy, cash=sources.cash,  commission=sources.commission)
stats = bt.optimize(
        fast_ema_period = range(20, 32, 2),
        slow_ema_period = range(60, 66, 1),
        constraint= lambda param: param.slow_ema_period > param.fast_ema_period,
        maximize="Equity Final [$]"
    )
print(stats)