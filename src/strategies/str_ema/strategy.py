from backtesting import Strategy
import src.indicators.i_ema as indicator

class ema_strategy(Strategy):
    #these emas doesnt count, im giving it as parameter to the strategy
    fast_ema_period = 0
    slow_ema_period = 0

    def init(self):
        self.fast_ema_indicator = self.I(indicator.i_ema, self.data, ema_period = self.fast_ema_period)
        self.slow_ema_indicator = self.I(indicator.i_ema, self.data, ema_period = self.slow_ema_period)

    def next(self):
        fast_ema = self.fast_ema_indicator[-1]
        slow_ema = self.slow_ema_indicator[-1]

        if self.position:
            if fast_ema < slow_ema:
                self.position.close()
        else:
             if fast_ema > slow_ema:
                self.buy(size=0.01)

