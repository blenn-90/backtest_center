# study which ema combination have the better results giving a in-sample dataset
# library imports
import sys
import src.strategies.sources as sources
import src.strategies.strategy_ema.str_ema_cross_w_atr as strategy
import src.utilities.get_data.binance_data as binance_data 
import src.utilities.get_data.tradingview_data as tradingview_data 
import src.utilities.noshare_data as noshare_data 
import src.classes.pair_data as pair_data
from src.classes.result_stats import *
from backtesting import Backtest
from os import listdir
from os.path import isfile, join
from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

print("----- START IN_SAMPLE BACKTESTING -----")
path = sys.path[noshare_data.project_sys_path_position] + "\\data"
# retrive all in-sample tradingview files
folder_tradingview = "tradingview_4h"
print("checking files from {folder} folder".format( folder = folder_tradingview ))
tradingview_data_file_set_is = [f for f in listdir(path + "\\" + folder_tradingview) if isfile(join(path + "\\" + folder_tradingview, f))]

# retrive all in-sample binance files
folder_binance = "binance_4h"
print("checking files from {folder} folder".format( folder = folder_binance ))
binance_data_file_set_is = [f for f in listdir(path + "\\" + folder_binance) if isfile(join(path + "\\" + folder_binance, f))]

#creating dataset of dataframe
list_pair_data = []
print("retrive data from {folder} folder".format( folder = folder_binance ))
for data_file in binance_data_file_set_is:
    #importing binance insample files
    data = binance_data.read_csv_data(path, folder_binance, data_file)
    list_pair_data.append(pair_data.create_pair_data(Path(data_file).stem, data_file, "binance", data, False))
print("retrive data from {folder} folder".format( folder = folder_binance ))
for data_file in tradingview_data_file_set_is:
    #importing tradinview insample files
    data = tradingview_data.read_csv_data(path, folder_tradingview, data_file)
    list_pair_data.append(pair_data.create_pair_data(Path(data_file).stem, data_file, "tradingview", data, True))
print("data is loaded")
#final list of insample data object, tradingview are primary beside binance data
print("creating in-sample dataset - no duplicate and tradingview priority")
insample_list = pair_data.getListNoDuplicate(list_pair_data)
#finire di implementare la classe pair data per capire ciclo1 o2 

# defining what data I want to optimize
# final equity will be decree the best emas in this case
def opt_func(series):
    return series["Equity Final [$]"]

# defining ema combination that will be backtested
fast_ema = [*range(80,82, 1)]
slow_ema = [*range(115, 120, 2)]
hardstop_list = np.arange(0.25, 1, 0.25)

ema_combinations = list(itertools.product(fast_ema, slow_ema, hardstop_list))
print(ema_combinations)
print("list of ema combinations to be tested: {ema_combinations}".format( ema_combinations=ema_combinations ))

#variable that trace the best ema equity
opt_function_final = 0
trades_best_combination = pd.DataFrame()
save_data_folder_is = ""

#list trades
df_all_trades = pd.DataFrame()

#heatmap
df_heatmap = pd.DataFrame(columns=["fast_ema", "slow_ema", "equity"])

#iterate all combination and backtesting it
for ema_combination in ema_combinations:
    print("start backtesting ema combination: {ema_combination}".format( ema_combination = ema_combination ))
    final_return_per_combination = 0
    final_exposure_time = 0
    df_result = pd.DataFrame(columns=["Pair","Size", "EntryPrice", "ExitPrice", "PnL", "ReturnPct", "EntryTime", "ExitTime", "Duration"])
   
    #backtesting all in-sample data and retriving final equity for each iteration 
    #analize binance data
    for key in insample_list:
        print("reading pair "+ key + ", source " + insample_list[key].source)
        #start checking how many cycle this pair did
        oldest_data = data[data.index < "2018-01-01"]
        insample_list[key].isFirstCycle = True
        if not oldest_data.empty:
            insample_list[key].isFirstCycle = False

        #running backtesting binance
        data = insample_list[key].data
        filter_data = data[ (data.index > "2015-01-01") & (data.index < "2018-02-01")]
        #check that file contain data and enought row to calculate ema
        if not filter_data.empty and len(filter_data) > ema_combination[0] and len(filter_data) > ema_combination[1] and len(filter_data) > sources.atr_length:
            bt = Backtest(filter_data, strategy.ema_cross_w_atr_strategy, cash=sources.cash,  commission=sources.commission)
            stats = bt.run(
                fast_ema_period = ema_combination[0],
                slow_ema_period =  ema_combination[1],
                hardstop_opt =  ema_combination[2],
            )
            final_return_per_combination = final_return_per_combination + stats["Return [%]"]
            final_exposure_time =  final_exposure_time + stats["Exposure Time [%]"]
            stats._trades['Pair'] = insample_list[key].pair
            stats._trades['IsFirstCycle'] = insample_list[key].isFirstCycle
            stats._trades['Data Source'] = insample_list[key].source
            df_result = pd.concat([df_result, stats._trades])
            #if you want to save plots use:
            #Path(save_data_folder_is +"\\plots\\").mkdir(parents=True, exist_ok=True)
            #bt.plot(resample=False, open_browser = False, filename = save_data_folder_is + "\\plots\\"+key+"_" + str(stats['_strategy']))

    print("combination {combination} -> return %: {return_perc}, exposure time: {time}".format(combination = ema_combination , return_perc = final_return_per_combination, time = final_exposure_time ))
    #calculate best combination that have highest return % / exposure time
    opt_function = final_return_per_combination / final_exposure_time

    #add combination to heatmap
    new_row_heatmap = [ema_combination[0], ema_combination[1], opt_function]
    df_heatmap.loc[len(df_heatmap)] = new_row_heatmap
    
    #checking if the current ema combination have better results then the best ema found
    if opt_function > opt_function_final:
        best_combination = ema_combination
        opt_function_final = opt_function
        trades_best_combination = df_result.copy()
        save_data_folder_is = "data\\result\\"+str(stats['_strategy'])+"\\in_sample"

#best combination data
print("best combination is: {best_combination} with a return % / exposure time % = {opt_function}".format(
    best_combination = best_combination, opt_function = opt_function))

#create trades excel for best combination
print("saving excel with trades of best combination strategy")
final_trades_best_combination = trades_best_combination.sort_values(by=['EntryTime'])
Path(save_data_folder_is).mkdir(parents=True, exist_ok=True)
with pd.ExcelWriter(save_data_folder_is + "\\trades.xlsx") as writer:
    final_trades_best_combination.to_excel(writer)

#heatmap
print("creating heatmap")
df_heatmap.set_index(df_heatmap.iloc[:, 0].name)
df_m = df_heatmap.groupby(["fast_ema","slow_ema"]).mean().unstack()
sns.heatmap(df_m)
plt.show()