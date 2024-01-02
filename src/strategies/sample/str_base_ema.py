#sample: ema base strategy using import from binance data
# library imports
import sys
import src.strategies.sources as sources
import src.utilities.get_data.tradingview_data as tradingview_data
import src.strategies.strategy_ema.str_ema_cross_w_atr as strategy
import pandas_ta as ta
import pandas as pd
import src.indicators.i_ema as indicator
import src.indicators.i_atr as indicator_atr
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
filtered_data = data[ (data.index > "2022-01-01") & (data.index < "2024-02-01") ]
#launching backtested
bt = Backtest(filtered_data, strategy.ema_cross_w_atr_strategy, cash=sources.cash,  commission=sources.commission)
stats = bt.run(
        fast_ema_period = 54,
        slow_ema_period = 198,
        hardstop_opt =  2,
        special_exit_opt = 1.5
    )

atr_df = indicator_atr.i_atr_v2(filtered_data, sources.atr_length)
# with pd.ExcelWriter("trades.xlsx") as writer:
#    stats['_trades'].to_excel(writer)  

print("----------- ATR DATAFRAME--------------")
print(atr_df)

print("----------- TRADES DATAFRAME --------------")
print(stats['_trades'])

print("----------- mergeee--------------")
print(stats['_trades'].merge(atr_df, how='left', on='EntryTime'))

#Path("data\\result\\"+str(stats['_strategy'])).mkdir(parents=True, exist_ok=True)
bt.plot(resample=False)
