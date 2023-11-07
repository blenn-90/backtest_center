import itertools

class ResultStat:
    #object it represents the result of a strategy backtested
    def __init__(self, 
        filename, 
        trades, 
        exposure_time_percentage, 
        equity_final_dollar, 
        return_percentage,
        buy_hold_return_percentage,
        sharpe_ratio,
        sortino_ratio,
        max_drawdown_percentage,
        win_rate_percentage,
        avg_trade_percentage,
        fast_ema_period,
        slow_ema_period
        ):
        self.filename = filename
        self.trades = trades
        self.exposure_time_percentage = exposure_time_percentage
        self.equity_final_dollar = equity_final_dollar
        self.return_percentage = return_percentage
        self.buy_hold_return_percentage = buy_hold_return_percentage
        self.sharpe_ratio = sharpe_ratio
        self.sortino_ratio = sortino_ratio
        self.max_drawdown_percentage = max_drawdown_percentage
        self.win_rate_percentage = win_rate_percentage
        self.avg_trade_percentage = avg_trade_percentage
        self.fast_ema_period = fast_ema_period
        self.slow_ema_period = slow_ema_period

    def stamp_result(self):
        return ("{filename}, "
                "# Trades {trades}, "
                "Exposure Time [%] {exposure_time_percentage}, " 
                "Equity Final {equity_final_dollar}, "
                "Return [%] {return_percentage}, "
                "Buy & Hold Return [%] {buy_hold_return_percentage}, "
                "Sharpe Ratio {sharpe_ratio}, "
                "Max. Drawdown [%] {max_drawdown_percentage}, "
                "Win Rate [%] {win_rate_percentage}, "
                "Avg. Trade [%] {avg_trade_percentage}, "
                "fast_ema_period {fast_ema_period}, "
                "slow_ema_period {slow_ema_period}"
                .format(

                filename= self.filename,
                trades=self.trades,
                exposure_time_percentage=self.exposure_time_percentage,
                equity_final_dollar= self.equity_final_dollar,
                return_percentage= self.return_percentage,
                buy_hold_return_percentage=self.buy_hold_return_percentage,
                sharpe_ratio=self.sharpe_ratio,
                max_drawdown_percentage=self.max_drawdown_percentage,
                win_rate_percentage=self.win_rate_percentage,
                avg_trade_percentage=self.avg_trade_percentage,
                fast_ema_period=self.fast_ema_period,
                slow_ema_period=self.slow_ema_period
        ))

def create_result_stat(filename, stats):
    return ResultStat(
            filename, 
            stats["# Trades"], 
            stats["Exposure Time [%]"], 
            stats["Equity Final [$]"],
            stats["Return [%]"],
            stats["Buy & Hold Return [%]"],
            stats["Sharpe Ratio"],
            stats["Sortino Ratio"],
            stats["Max. Drawdown [%]"],
            stats["Win Rate [%]"],
            stats["Avg. Trade [%]"],
            stats._strategy.fast_ema_period, 
            stats._strategy.slow_ema_period 
        )

def get_ema_mean(result_stats):
    counter = 0
    fast_ema_sum = 0
    slow_ema_sum = 0
    for result_stat in result_stats:
        fast_ema_sum = fast_ema_sum + result_stat.fast_ema_period
        slow_ema_sum = slow_ema_sum + result_stat.slow_ema_period
        counter = counter + 1
    
    if counter == 0:
        return [fast_ema_sum, slow_ema_sum]

    return [fast_ema_sum/counter, slow_ema_sum/counter]


def get_equity_final(result_stats):
    equity_final_sum = 0
    for result_stat in result_stats:
        equity_final_sum = equity_final_sum + result_stat.equity_final_dollar
    
    return equity_final_sum

def get_all_ema_combinantion(result_stats):
    all_ema_combinantion = []
    for result_stat in result_stats:
        ema_combinantion = [result_stat.fast_ema_period, result_stat.slow_ema_period]
        all_ema_combinantion.append(ema_combinantion)

    all_ema_combinantion.sort()
    return list(all_ema_combinantion for all_ema_combinantion,_ in itertools.groupby(all_ema_combinantion))
