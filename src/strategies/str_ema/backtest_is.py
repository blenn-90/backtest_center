# study which ema combination have the better results giving a in-sample dataset
# library imports
import sys
import src.strategies.sources as sources
import src.strategies.str_ema.strategy as strategy
import src.utilities.get_data.binance_data as binance_data 
import src.utilities.noshare_data as noshare_data 
from src.classes.result_stats import *
from backtesting import Backtest
from os import listdir
from os.path import isfile, join
from pathlib import Path

# retrive all in-sample files
path = sys.path[noshare_data.project_sys_path_position] + "\\data"
timeframe = "in_sample"
data_file_set_is = [f for f in listdir(path + "\\" + timeframe) if isfile(join(path + "\\" + timeframe, f))]
result_stats_is = []

# defining what data I want to optimize
# final equity will be decree the best emas in this case
def opt_func(series):
    return series["Equity Final [$]"]

# defining ema combination that will be backtested
fast_ema = [*range(9, 11, 1)]
slow_ema = [*range(18, 21, 1)]
ema_combinations = list(itertools.product(fast_ema, slow_ema))

#variable that trace the best ema equity
final_equity_best_combination = 0
#iterate all combination and backtesting it
for ema_combination in ema_combinations:
    final_equity_per_combination = 0
    #backtesting all in-sample data and retriving final equity for each iteration 
    for data_file in data_file_set_is:
        data = binance_data.read_csv_data(path, timeframe, data_file)
        #running backtesting
        bt = Backtest(data, strategy.ema_strategy, cash=sources.cash,  commission=sources.commission)
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

print(best_combination)