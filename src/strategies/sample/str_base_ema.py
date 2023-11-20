#sample: ema base strategy using import from binance data
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
stats, heatmap = bt.optimize(
        fast_ema_period = range(20, 32, 2),
        slow_ema_period = range(60, 66, 1),
        constraint= lambda param: param.slow_ema_period > param.fast_ema_period,
        maximize="Equity Final [$]",
        return_heatmap = True
    )
#plot backtest result
hm = heatmap.groupby(["fast_ema_period","slow_ema_period"]).mean().unstack()
sns.heatmap(hm)
plt.show()

with pd.ExcelWriter("trades.xlsx") as writer:
    stats['_trades'].to_excel(writer)  
print(stats)
Path("data\\result\\"+str(stats['_strategy'])).mkdir(parents=True, exist_ok=True)
bt.plot(resample=False, filename = "data\\result\\"+str(stats['_strategy']) + "\\"+str(stats['_strategy']))
