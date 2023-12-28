# backtesting an out-of-sample dataset
# library imports
import sys
import pandas as pd
import src.strategies.sources as sources
import src.strategies.strategy_ema.str_ema_cross_w_atr as strategy
import src.utilities.show_result as show_result
import src.classes.result_stats as result_stats_printer
import src.utilities.get_data.kucoin_data as kucoin_data
import src.utilities.noshare_data as noshare_data 
from backtesting import Backtest, Strategy
from os import listdir
from os.path import isfile, join
from pathlib import Path
from datetime import datetime

print("----- START OUT_OF_SAMPLE BACKTESTING -----")
# retrive all out_of_sample files
timeframe = "kucoin_4h"
print("retrive data from {timeframe} folder".format( timeframe = timeframe ))
path = sys.path[noshare_data.project_sys_path_position] + "\\data"

data_file_set_oos = [f for f in listdir(path + "\\" + timeframe) if isfile(join(path + "\\" + timeframe, f))]
print("found {number} pairs".format( number = data_file_set_oos.count ))

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

# defining some basic object used in the backtest
df_result = pd.DataFrame(columns=["Pair","Size", "EntryPrice", "ExitPrice", "PnL", "ReturnPct", "EntryTime", "ExitTime", "Duration", "Born_at_cycle"])
#best combination from IS backtesting
fast_ema_period = 72
slow_ema_period = 288
hardstop_opt = 2
special_exit_opt = 5
print("ema combination to be tested: {fast_ema_period}, {slow_ema_period}".format( fast_ema_period=fast_ema_period, slow_ema_period=slow_ema_period ))

save_data_folder_oos = ""
final_return_per_combination = 0
final_exposure_time = 0
final_equity = 0
final_total_trades = 0
final_total_win = 0

#iterate all files and backtest it
for data_file in data_file_set_oos:
    data = kucoin_data.read_csv_data(path, timeframe, data_file)
    #running backtesting
    filter_data = data[ data.index > "2020-09-09"]
    strategy_name = ""
    #check if filtered data are not empty
    if not filter_data.empty and len(filter_data) > fast_ema_period and len(filter_data) > slow_ema_period and len(filter_data) > sources.atr_length and slow_ema_period != fast_ema_period:
        #launching backtest for the filtered data
        bt = Backtest(filter_data, strategy.ema_cross_w_atr_strategy, cash=sources.cash,  commission=sources.commission)
        stats = bt.run(
            fast_ema_period = fast_ema_period,
            slow_ema_period = slow_ema_period,
            hardstop_opt = hardstop_opt,
            special_exit_opt = special_exit_opt
        )
        #saving results for the current file
        if stats['# Trades'] > 0 :
            print("Found {count} trades, backtesting {filename}".format( count = stats['# Trades'], filename = Path(data_file).stem ))
            stats._trades['Pair'] = Path(data_file).stem 
            
            #setting cycle data, if no data found set it as new coin
            if cycle_data_df[cycle_data_df.pair==Path(data_file).stem].empty: 
                stats._trades['Born_at_cycle'] = 4
            else:
                stats._trades['Born_at_cycle'] = cycle_data_df[cycle_data_df.pair==Path(data_file).stem].born_at_cycle.item()
            

            df_result = pd.concat([df_result, stats._trades])
            final_return_per_combination = final_return_per_combination + stats["Return [%]"]
            final_exposure_time =  final_exposure_time + stats["Exposure Time [%]"]
            final_equity = final_equity + stats["Equity Final [$]"]
            final_total_trades = final_total_trades + stats["# Trades"]
            if(stats["# Trades"] != 0):
                final_total_win = final_total_win + (stats["# Trades"] * stats["Win Rate [%]"] / 100)
        else:
            print("Found 0 trades, backtesting "+ Path(data_file).stem)
      
        strategy_name = str(stats['_strategy'])

    #creating the object to represent the result data
    save_data_folder_oos = "data\\result\\"+strategy_name+"\\out_of_sample"

        #calculate best combination that have highest return % / exposure time
    if final_exposure_time == 0:
        #no trades found
        print("no trades detected")
    else:
        opt_function = final_return_per_combination / final_exposure_time

#create excel trades
Path(save_data_folder_oos).mkdir(parents=True, exist_ok=True)
now = datetime.now()
current_time = now.strftime("%H%M%S")
final_df = df_result.sort_values(by=['EntryTime'])
with pd.ExcelWriter(save_data_folder_oos + "\\trades.xlsx") as writer:
    final_df.to_excel(writer)  

print (
        "--- Results MultiAssets ---\n"
            "# Assets: {number_of_assets} \n"
            "# Trades: {trades} \n"
            "Equity Final [$] : {equity_final_dollar} \n"
            "Return [%]: {final_return_per_combination} \n"
            "Exposure Time [%]: {exposuretime_percentage} \n"
            "Return [%] / Exposure Time [%]: {opt_function} \n"
            "Win Rate [%]: {win_rate_percentage} \n"
        .format(
            number_of_assets = len(data_file_set_oos),
            trades = str(len(final_df.index)),
            equity_final_dollar = str(round(final_equity, 2)),
            final_return_per_combination =  str(round(final_return_per_combination)),
            exposuretime_percentage =  str(round(final_exposure_time)),                         
            opt_function = str(round(opt_function)),    
            win_rate_percentage = str(round( final_total_win/final_total_trades*100, 2))
        )
    )    

# show results passing list of trades
#print(show_result.show_multiassets_results(df_result, len(data_file_set_oos), fast_ema_period = fast_ema_period, slow_ema_period = slow_ema_period))

print("----- END OUT_OF_SAMPLE BACKTESTING -----")