#sample: ema base strategy using import from binance data
# library imports
import sys
import src.strategies.sources as sources
import src.utilities.get_data.tradingview_data as tradingview_data
import src.strategies.strategy_ema.str_ema_cross_w_atr as strategy
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
import numpy as np

#retrive data / use tradinview_data in utilities if data come from tradingview
path = sys.path[noshare_data.project_sys_path_position] + "\\data"
timeframe = "tradingview_4h"
filename = "ADAUSD.csv"
data = tradingview_data.read_csv_data(path, timeframe, filename)
print(data)
#launching backtested
bt = Backtest(data[ (data.index > "2015-01-01") & (data.index < "2024-02-01") ], strategy.ema_cross_w_atr_strategy, cash=sources.cash,  commission=sources.commission)
stats = bt.run(
        fast_ema_period = 54,
        slow_ema_period = 198,
        hardstop_opt =  2,
        special_exit_opt = 1.5
    )

# with pd.ExcelWriter("trades.xlsx") as writer:
#    stats['_trades'].to_excel(writer)  
#print(stats)
#Path("data\\result\\"+str(stats['_strategy'])).mkdir(parents=True, exist_ok=True)
bt.plot(resample=False)
