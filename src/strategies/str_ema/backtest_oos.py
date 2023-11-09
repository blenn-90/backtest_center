#%% importing
import sys
sys.path.append("c:\\Users\\Alessandro\\Desktop\\python\\backtest_center_v2" + "\\src")
from utilities.noshare_data import *
from strategies.str_ema.strategy import *
from utilities.show_result import *
from utilities.import_data import *
from classes.result_stats import *
from backtesting import Backtest, Strategy
from os import listdir
from os.path import isfile, join
from pathlib import Path
from utilities.binance_data import *

#%% data out-of-sample
path = project_path + "\\data"
timeframe = "out_of_sample"
data_file_set_oos = [f for f in listdir(path + "\\" + timeframe) if isfile(join(path + "\\" + timeframe, f))]
result_stats_oos = []
df_result = pd.DataFrame(columns=["Size", "EntryPrice", "ExitPrice", "PnL", "ReturnPct", "EntryTime", "ExitTime", "Duration"])
fast_ema_period = 9
slow_ema_period = 19

#%% backtest out-of-sample
for data_file in data_file_set_oos:
    data = read_csv_data(path, timeframe, data_file)
    print(data)
    bt = Backtest(data, ema_strategy, cash=cash,  commission=commission)
    stats = bt.optimize(
        fast_ema_period = fast_ema_period,
        slow_ema_period = slow_ema_period
    )
    bt.plot()
    result_stats = create_result_stat(data_file, stats)
    result_stats_oos.append(result_stats)
    stats._trades['pair'] = data_file
    df_result = pd.concat([df_result, stats._trades])

#%% show results passing list of trades
print(show_multiassets_results(df_result, len(data_file_set_oos), fast_ema_period = fast_ema_period, slow_ema_period = slow_ema_period))