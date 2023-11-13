#sample: ema base strategy using import from binance data
# library imports
import sys
print(sys.path)
import src.strategies.sources as sources
import src.utilities.get_data.binance_data as binance_data
import src.strategies.strategy_ema.str_ema_cross_w_hardstop as strategy
import pandas_ta as ta
import src.indicators.i_ema as indicator
import src.utilities.noshare_data as noshare_data
from backtesting import Backtest, Strategy
from backtesting.lib import resample_apply
from os import listdir
from os.path import isfile, join
from pathlib import Path  


#retrive data / use tradinview_data in utilities if data come from tradingview
path = sys.path[noshare_data.project_sys_path_position] + "\\data"
timeframe = "in_sample"
filename = "AAVEUSDT.csv"
data = binance_data.read_csv_data(path, timeframe, filename)
print(data)
#launching backtested
bt = Backtest(data[data.index > "2021-01-01"], strategy.ema_strategy, cash=sources.cash,  commission=sources.commission)
stats = bt.optimize(
        fast_ema_period = range(8, 12, 1),
        slow_ema_period = range(12, 14, 1),
        constraint= lambda param: param.slow_ema_period > param.fast_ema_period,
        maximize="Equity Final [$]"
    )
#plot backtest result
bt.plot(resample=False)