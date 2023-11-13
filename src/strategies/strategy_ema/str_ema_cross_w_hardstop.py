from backtesting import Strategy
import src.indicators.i_ema as indicator

class ema_strategy(Strategy):
    #these emas doesnt count, im giving it as parameter to the strategy
    fast_ema_period = 0
    slow_ema_period = 0
    hardstop_percentage = 10

    def init(self):
        #calculate fast and slow ema matrix
        self.fast_ema_indicator = self.I(indicator.i_ema, self.data, ema_period = self.fast_ema_period)
        self.slow_ema_indicator = self.I(indicator.i_ema, self.data, ema_period = self.slow_ema_period)

    def next(self):
        #get last fast and slow ema from indicator
        fast_ema = self.fast_ema_indicator[-1]
        slow_ema = self.slow_ema_indicator[-1]
        #get last close value
        last_close = self.data.Close[-1]

        if self.position:
            if fast_ema < slow_ema:
                self.position.close()
        else:
             if fast_ema > slow_ema:
                #buy with hardstop below a certain percetage
                stoploss = last_close - (last_close * self.hardstop_percentage/100)
                self.buy(size=0.01, sl= stoploss)
