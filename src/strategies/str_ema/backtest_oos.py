#%% importing
import sys
import pandas as pd
import src.strategies.sources as sources
import src.strategies.str_ema.strategy as strategy
import src.utilities.show_result as show_result
import src.classes.result_stats as result_stats_printer
import src.utilities.binance_data as binance_data
from backtesting import Backtest, Strategy
from os import listdir
from os.path import isfile, join
from pathlib import Path


#%% data out-of-sample
path = sys.path[1] + "\\data"
timeframe = "out_of_sample"
data_file_set_oos = [f for f in listdir(path + "\\" + timeframe) if isfile(join(path + "\\" + timeframe, f))]
result_stats_oos = []
df_result = pd.DataFrame(columns=["Size", "EntryPrice", "ExitPrice", "PnL", "ReturnPct", "EntryTime", "ExitTime", "Duration"])
fast_ema_period = 9
slow_ema_period = 19

#%% backtest out-of-sample
for data_file in data_file_set_oos:
    data = binance_data.read_csv_data(path, timeframe, data_file)
    print(data)
    bt = Backtest(data, strategy.ema_strategy, cash=sources.cash,  commission=sources.commission)
    stats = bt.optimize(
        fast_ema_period = fast_ema_period,
        slow_ema_period = slow_ema_period
    )
    bt.plot()
    result_stats = result_stats_printer.create_result_stat(data_file, stats)
    result_stats_oos.append(result_stats)
    stats._trades['pair'] = data_file
    df_result = pd.concat([df_result, stats._trades])

#%% show results passing list of trades
print(show_result.show_multiassets_results(df_result, len(data_file_set_oos), fast_ema_period = fast_ema_period, slow_ema_period = slow_ema_period))