#importing
import sys
from strategies.sources import *
sys.path.append("c:\\Users\\Alessandro\\Desktop\\python\\backtest_center_v2" + "\\src")
from backtesting import Strategy
from indicators.i_ema import *

class ema_strategy(Strategy):
    fast_ema_period = 7
    slow_ema_period = 18

    def init(self):
        self.fast_ema_indicator = self.I(i_ema, self.data, ema_period = self.fast_ema_period)
        self.slow_ema_indicator = self.I(i_ema, self.data, ema_period = self.slow_ema_period)

    def next(self):
        fast_ema = self.fast_ema_indicator[-1]
        slow_ema = self.slow_ema_indicator[-1]

        if self.position:
            if fast_ema < slow_ema:
                self.position.close()
        else:
             if fast_ema > slow_ema:
                self.buy(size=0.01)

