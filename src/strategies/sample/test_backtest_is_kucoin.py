# study which ema combination have the better results giving a in-sample dataset
# library imports
import sys
import src.strategies.sources as sources
import src.utilities.sources as ut_sources
import src.strategies.strategy_ema.str_ema_cross_w_atr as strategy
import src.utilities.get_data.binance_data as binance_data 
import src.utilities.get_data.kucoin_data as kucoin_data 
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
import src.indicators.i_atr as indicator_atr

print("----- START IN_SAMPLE BACKTESTING -----")
path = sys.path[noshare_data.project_sys_path_position] + "\\data"

# retrive all in-sample tradingview files
kucoin_file_set_is = kucoin_data.get_file_data_set()
folder_tradingview = "kucoin_4h"

#creating dataset of dataframe
insample_list = kucoin_data.get_insample_list(kucoin_file_set_is, path, folder_tradingview)


print("data is loaded")
# defining ema combination that will be backtested
fast_ema = [*range(60, 66, 6)]
slow_ema = [*range(276, 282, 6)]
hardstop_list = np.arange(2.6, 2.7, 0.5)
special_exit_opt_list = np.arange(5, 7, 1)

ema_combinations = list(itertools.product(fast_ema, slow_ema, hardstop_list, special_exit_opt_list))
print("list of ema combinations to be tested: {ema_combinations}".format( ema_combinations=ema_combinations ))

#variable that trace the best ema equity
opt_function_final = -99999
trades_best_combination = pd.DataFrame()
save_data_folder_is = ""

#list trades
df_all_trades = pd.DataFrame()

#excel result export
df_excel_report = pd.DataFrame(columns=["ema_combination", "equity", "return %", "exposure time %", "return % / exposure time %", "total trades", "win rate %"])

#heatmap
dictionary_heatmap = {}
dictionary_heatmap_count = 0
for hardstop in hardstop_list:
        dictionary_heatmap[hardstop] = pd.DataFrame(columns=["fast_ema", "slow_ema", "equity"])
        dictionary_heatmap_count = dictionary_heatmap_count + 1

#read cycles data file
cycle_data_df = pd.read_csv(
        path + "\\cycles_data\\cycles_data.csv",
        usecols=[0,1],
        names=["pair",'born_at_cycle'],
        skiprows=[0]
    )
    #print(data)
    #setting dataframe index
print(cycle_data_df)

#iterate all combination and backtesting it
i_combs = 0
for ema_combination in ema_combinations:
    print("start backtesting ema combination: {ema_combination}".format( ema_combination = ema_combination ))
    final_return_per_combination = 0
    final_exposure_time = 0
    final_equity = 0
    final_total_trades = 0
    final_total_win = 0
    
    df_result = pd.DataFrame(columns=["Pair","Size", "EntryPrice", "ExitPrice", "PnL", "ReturnPct", "EntryTime", "ExitTime", "Duration", "ATR"])
   
    #backtesting all in-sample data and retriving final equity for each iteration 
    #analize binance data
    for key in insample_list:
        #setting cycle data, if no data found set it as new coin
        if cycle_data_df[cycle_data_df.pair==Path(key).stem].empty or cycle_data_df[cycle_data_df.pair==Path(key).stem].born_at_cycle.item() !=3:
           continue

        data = insample_list[key].data
        #start checking how many cycle this pair did
        oldest_data = data[data.index < "2019-11-01"]
        insample_list[key].isFirstCycle = True
        if not oldest_data.empty:
            insample_list[key].isFirstCycle = False

        #running backtesting binance
        
        filter_data = data[ (data.index > "2019-11-01") & (data.index < "2022-02-01")]
        #check that file contain data and enought row to calculate ema
        if not filter_data.empty and len(filter_data) > ema_combination[0] and len(filter_data) > ema_combination[1] and len(filter_data) > sources.atr_length and ema_combination[0] < ema_combination[1]:
            bt = Backtest(filter_data, strategy.ema_cross_w_atr_strategy, cash=sources.cash,  commission=sources.commission)
            stats = bt.run(
                fast_ema_period = ema_combination[0],
                slow_ema_period =  ema_combination[1],
                hardstop_opt =  ema_combination[2],
                special_exit_opt =  ema_combination[3]
            )
            final_return_per_combination = final_return_per_combination + stats["Return [%]"]
            final_exposure_time =  final_exposure_time + stats["Exposure Time [%]"]
            final_equity = final_equity + stats["Equity Final [$]"]
            final_total_trades = final_total_trades + stats["# Trades"]
            if(stats["# Trades"] != 0):
                final_total_win = final_total_win + (stats["# Trades"] * stats["Win Rate [%]"] / 100)
            stats._trades['Pair'] = insample_list[key].pair
            stats._trades['IsFirstCycle'] = insample_list[key].isFirstCycle
            stats._trades['Data Source'] = insample_list[key].source
            atr_df = indicator_atr.i_atr_v2(filter_data, sources.atr_length)
            trades_df = stats['_trades'].merge(atr_df, how='left', on='EntryTime')
            df_result = (df_result.copy() if stats._trades.empty else stats._trades.copy() if df_result.empty else pd.concat([df_result, trades_df])) # if both DataFrames non empty)
            #if you want to save plots use:
            #Path(save_data_folder_is +"\\plots\\").mkdir(parents=True, exist_ok=True)
            #bt.plot(resample=False, open_browser = True, filename = save_data_folder_is + "\\plots\\"+key+"_" + str(stats['_strategy']))

    
    #calculate best combination that have highest return % / exposure time
    if final_exposure_time == 0:
        #no trades found
        print("no trades detected")
    else:
        opt_function = final_return_per_combination / final_exposure_time
        new_row_heatmap = [ema_combination[0], ema_combination[1], opt_function]
        print("combination {combination} -> return %: {return_perc}, exposure time: {time}, result: {result}".format(combination = ema_combination , return_perc = final_return_per_combination, time = final_exposure_time, result = opt_function ))

        df_heatmap_current_combination = dictionary_heatmap.get(ema_combination[2])
        df_heatmap_current_combination.loc[len(df_heatmap_current_combination)] = new_row_heatmap
        dictionary_heatmap.update({ema_combination[2]: df_heatmap_current_combination})
        
        #checking if the current ema combination have better results then the best ema found
        if opt_function > opt_function_final:
            best_combination = ema_combination
            opt_function_final = opt_function
            trades_best_combination = df_result.copy()
            save_data_folder_is = "data\\result\\"+str(stats['_strategy'])+"\\in_sample"
        
        df_excel_report.loc[i_combs] = [ema_combination, ut_sources.fun_format_2decimal(final_equity), ut_sources.fun_format_2decimal(final_return_per_combination), ut_sources.fun_format_2decimal(final_exposure_time), ut_sources.fun_format_4decimal(opt_function), final_total_trades, ut_sources.fun_format_2decimal(final_total_win/final_total_trades*100)]
        i_combs = i_combs + 1

#best combination data
print("best combination is: {best_combination} with a return % / exposure time % = {opt_function}".format(
    best_combination = best_combination, opt_function = opt_function_final))

#create trades excel for best combination
print("saving excel with trades of best combination strategy")
final_trades_best_combination = trades_best_combination.sort_values(by=['EntryTime'])
Path(save_data_folder_is).mkdir(parents=True, exist_ok=True)
with pd.ExcelWriter(save_data_folder_is + "\\trades.xlsx") as writer:
    final_trades_best_combination.to_excel(writer)

#generate excel report 
print("generate excel report")
df_excel_report = df_excel_report.sort_values(by=['return % / exposure time %'], ascending=False)
with pd.ExcelWriter(save_data_folder_is + "\\combination_results.xlsx") as writer:
    df_excel_report.to_excel(writer)

#heatmap
print("creating heatmap")
#multiplot heatmap
if dictionary_heatmap_count > 1:
    fig, axs = plt.subplots(ncols=dictionary_heatmap_count)
    i=0
    for key in dictionary_heatmap:
        df_heatmap = dictionary_heatmap[key]
        df_heatmap.set_index(df_heatmap.iloc[:, 0].name)
        df_m = df_heatmap.groupby(["fast_ema","slow_ema"]).mean().unstack()
        sns.heatmap(df_m, ax=axs[i])
        i=i+1
#single plot heatmap
else:
    for key in dictionary_heatmap:
        df_heatmap = dictionary_heatmap[key]
        df_heatmap.set_index(df_heatmap.iloc[:, 0].name)
        df_m = df_heatmap.groupby(["fast_ema","slow_ema"]).mean().unstack()
        sns.heatmap(df_m)
        plt.title(str(key) + '_hardstop', fontsize =20)

plt.show()
print("----- END IN_SAMPLE BACKTESTING -----")

