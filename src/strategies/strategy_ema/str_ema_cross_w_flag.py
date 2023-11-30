from backtesting import Strategy
import src.indicators.i_ema as indicator
import src.indicators.i_flag as indicator_flag

class ema_cross_strategy(Strategy):
    #these emas doesnt count, im giving it as parameter to the strategy
    fast_ema_period = 0
    slow_ema_period = 0

    def init(self):
        #calculate fast and slow ema matrix
        self.fast_ema_indicator = self.I(indicator.i_ema, self.data, ema_period = self.fast_ema_period)
        self.slow_ema_indicator = self.I(indicator.i_ema, self.data, ema_period = self.slow_ema_period)
        self.flag = self.I(indicator_flag.i_flag, self.data, scatter = True, overlay=True, color="#ff4040")

    def next(self):
        #get next fast and slow ema from indicator
        fast_ema = self.fast_ema_indicator[-1]
        slow_ema = self.slow_ema_indicator[-1]

        if self.position:
            if fast_ema < slow_ema:
                self.position.close()
        else:
             if fast_ema > slow_ema:
                self.buy(size=0.01)

