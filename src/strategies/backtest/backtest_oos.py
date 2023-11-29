# backtesting an out-of-sample dataset
# library imports
import sys
import pandas as pd
import src.strategies.sources as sources
import src.strategies.strategy_ema.str_ema_cross_w_atr as strategy
import src.utilities.show_result as show_result
import src.classes.result_stats as result_stats_printer
import src.utilities.get_data.binance_data as binance_data
import src.utilities.noshare_data as noshare_data 
from backtesting import Backtest, Strategy
from os import listdir
from os.path import isfile, join
from pathlib import Path
from datetime import datetime

print("----- START OUT_OF_SAMPLE BACKTESTING -----")
# retrive all out_of_sample files
timeframe = "binance_4h"
print("retrive data from {timeframe} folder".format( timeframe = timeframe ))
path = sys.path[noshare_data.project_sys_path_position] + "\\data"

data_file_set_oos = [f for f in listdir(path + "\\" + timeframe) if isfile(join(path + "\\" + timeframe, f))]
print("found {number} pairs".format( number = data_file_set_oos.count ))

# defining some basic object used in the backtest
df_result = pd.DataFrame(columns=["Pair","Size", "EntryPrice", "ExitPrice", "PnL", "ReturnPct", "EntryTime", "ExitTime", "Duration"])
#best combination from IS backtesting
fast_ema_period = 102
slow_ema_period = 138
hardstop_opt = 2
print("ema combination to be tested: {fast_ema_period}, {slow_ema_period}".format( fast_ema_period=fast_ema_period, slow_ema_period=slow_ema_period ))

save_data_folder_oos = ""

#iterate all files and backtest it
for data_file in data_file_set_oos:
    data = binance_data.read_csv_data(path, timeframe, data_file)
    #running backtesting
    filter_data = data[ data.index > "2022-01-01"]
    strategy_name = ""
    #check if filtered data are not empty
    if not filter_data.empty and len(filter_data) > fast_ema_period and len(filter_data) > slow_ema_period and len(filter_data) > sources.atr_length and slow_ema_period != fast_ema_period:
        #launching backtest for the filtered data
        bt = Backtest(filter_data, strategy.ema_cross_w_atr_strategy, cash=sources.cash,  commission=sources.commission)
        stats = bt.run(
            fast_ema_period = fast_ema_period,
            slow_ema_period = slow_ema_period,
            hardstop_opt = hardstop_opt
        )
        #saving results for the current file
        if stats['# Trades'] > 0 :
            print("Found {count} trades, backtesting {filename}".format( count = stats['# Trades'], filename = Path(data_file).stem ))
            stats._trades['Pair'] = Path(data_file).stem
            df_result = pd.concat([df_result, stats._trades])
        else:
            print("Found 0 trades, backtesting "+ Path(data_file).stem)
      
        strategy_name = str(stats['_strategy'])

    #creating the object to represent the result data
    save_data_folder_oos = "data\\result\\"+strategy_name+"\\out_of_sample"

#create excel trades
Path(save_data_folder_oos).mkdir(parents=True, exist_ok=True)
now = datetime.now()
current_time = now.strftime("%H%M%S")
final_df = df_result.sort_values(by=['EntryTime'])
with pd.ExcelWriter(save_data_folder_oos + "\\trades.xlsx") as writer:
    final_df.to_excel(writer)  

# show results passing list of trades
print(show_result.show_multiassets_results(df_result, len(data_file_set_oos), fast_ema_period = fast_ema_period, slow_ema_period = slow_ema_period))