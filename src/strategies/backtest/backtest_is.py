# study which ema combination have the better results giving a in-sample dataset
# library imports
import sys
import src.strategies.sources as sources
import src.strategies.strategy_ema.str_ema_cross_w_hardstop as strategy
import src.utilities.get_data.binance_data as binance_data 
import src.utilities.noshare_data as noshare_data 
from src.classes.result_stats import *
from backtesting import Backtest
from os import listdir
from os.path import isfile, join
from pathlib import Path

print("----- START IN_SAMPLE BACKTESTING -----")
# retrive all in-sample files
timeframe = "binance_1d"
print("retrive data from {timeframe} folder".format( timeframe = timeframe ))
path = sys.path[noshare_data.project_sys_path_position] + "\\data"
data_file_set_is = [f for f in listdir(path + "\\" + timeframe) if isfile(join(path + "\\" + timeframe, f))]

print("found {number} pairs".format( number = data_file_set_is.count ))
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
#iterate all combination and backtesting it
for ema_combination in ema_combinations:
    print("start backtesting ema combination: {ema_combination}".format( ema_combination=ema_combination ))
    final_equity_per_combination = 0
    #backtesting all in-sample data and retriving final equity for each iteration 
    for data_file in data_file_set_is:
        data = binance_data.read_csv_data(path, timeframe, data_file)
        print("reading pair: {data_file}".format( data_file=data_file ))
        #running backtesting
        filter_data = data[data.index < "2020-01-01"]
        #check that file contain data and enought row to calculate ema
        if not filter_data.empty and len(filter_data) > ema_combination[0] and len(filter_data) > ema_combination[1]:
            bt = Backtest(filter_data, strategy.ema_strategy, cash=sources.cash,  commission=sources.commission)
            stats = bt.run(
                fast_ema_period = ema_combination[0],
                slow_ema_period =  ema_combination[1],
            )
            final_equity_per_combination = final_equity_per_combination + stats["Equity Final [$]"]
    print("combination {ema1}, {ema2} -> {equity}".format(ema1 = ema_combination[0], ema2 = ema_combination[1], equity = final_equity_per_combination))
    #checking if the current ema combination have better results then the best ema found
    if final_equity_per_combination > final_equity_best_combination:
        best_combination = ema_combination
        final_equity_best_combination = final_equity_per_combination

print("best combination is: {best_combination} with a final equity = {final_equity_best_combination}".format(
    best_combination = best_combination, final_equity_best_combination = final_equity_best_combination))
