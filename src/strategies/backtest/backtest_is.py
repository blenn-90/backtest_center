# study which ema combination have the better results giving a in-sample dataset
# library imports
import sys
import src.strategies.sources as sources
import src.strategies.strategy_ema.str_ema_cross_w_hardstop as strategy
import src.utilities.get_data.binance_data as binance_data 
import src.utilities.get_data.tradingview_data as tradingview_data 
import src.utilities.noshare_data as noshare_data 
from src.classes.result_stats import *
from backtesting import Backtest
from os import listdir
from os.path import isfile, join
from pathlib import Path
import pandas as pd
from datetime import datetime

print("----- START IN_SAMPLE BACKTESTING -----")
# retrive all in-sample binance files
folder_binance = "in_sample_binance"
print("retrive data from {folder} folder".format( folder = folder_binance ))
path = sys.path[noshare_data.project_sys_path_position] + "\\data"
binance_data_file_set_is = [f for f in listdir(path + "\\" + folder_binance) if isfile(join(path + "\\" + folder_binance, f))]
print("found {number} binance pairs".format( number = binance_data_file_set_is.count ))

# retrive all in-sample tradingview files
folder_tradingview = "in_sample_tradingview"
print("retrive data from {folder} folder".format( folder = folder_tradingview ))
tradingview_data_file_set_is = [f for f in listdir(path + "\\" + folder_tradingview) if isfile(join(path + "\\" + folder_tradingview, f))]
print("found {number} tradingview pairs".format( number = tradingview_data_file_set_is.count ))

#creating dataset of dataframe
dataset = {}
for data_file in binance_data_file_set_is:
    #importing binance insample files
    data = binance_data.read_csv_data(path, folder_binance, data_file)
    dataset[data_file] = data

for data_file in tradingview_data_file_set_is:
    #importing tradinview insample files
    data = tradingview_data.read_csv_data(path, folder_tradingview, data_file)
    dataset[data_file] = data

# defining what data I want to optimize
# final equity will be decree the best emas in this case
def opt_func(series):
    return series["Equity Final [$]"]

# defining ema combination that will be backtested
fast_ema = [*range(9, 11, 1)]
slow_ema = [*range(18, 21, 1)]
ema_combinations = list(itertools.product(fast_ema, slow_ema))
print("list of ema combinations to be tested: {ema_combinations}".format( ema_combinations=ema_combinations ))

#variable that trace the best ema equity
final_equity_best_combination = 0
#list trades
df_all_trades = pd.DataFrame()

#iterate all combination and backtesting it
for ema_combination in ema_combinations:
    print("start backtesting ema combination: {ema_combination}".format( ema_combination=ema_combination ))
    final_equity_per_combination = 0

    df_result = pd.DataFrame(columns=["Pair","Size", "EntryPrice", "ExitPrice", "PnL", "ReturnPct", "EntryTime", "ExitTime", "Duration"])
    #backtesting all in-sample data and retriving final equity for each iteration 
    #analize binance data
    for key in dataset:
        print("reading pair: "+ key)
        #running backtesting binance
        data = dataset[key]
        filter_data = data[data.index < "2020-01-01"]
        #check that file contain data and enought row to calculate ema
        if not filter_data.empty and len(filter_data) > ema_combination[0] and len(filter_data) > ema_combination[1]:
            bt = Backtest(filter_data, strategy.ema_strategy, cash=sources.cash,  commission=sources.commission)
            stats = bt.run(
                fast_ema_period = ema_combination[0],
                slow_ema_period =  ema_combination[1],
            )
            final_equity_per_combination = final_equity_per_combination + stats["Equity Final [$]"]
            stats._trades['Pair'] = Path(data_file).stem
            df_result = pd.concat([df_result, stats._trades])

    now = datetime.now()
    current_time = now.strftime("%H%M%S")
    final_df = df_result.sort_values(by=['EntryTime'])
    with pd.ExcelWriter(".\\data\\result\\is_trades\\is_trades_ema"+str(ema_combination)+"_"+current_time+".xlsx") as writer:
        final_df.to_excel(writer)  
        
    print("combination {ema1}, {ema2} -> {equity}".format(ema1 = ema_combination[0], ema2 = ema_combination[1], equity = final_equity_per_combination))
    #checking if the current ema combination have better results then the best ema found
    if final_equity_per_combination > final_equity_best_combination:
        best_combination = ema_combination
        final_equity_best_combination = final_equity_per_combination

print("best combination is: {best_combination} with a final equity = {final_equity_best_combination}".format(
    best_combination = best_combination, final_equity_best_combination = final_equity_best_combination))
