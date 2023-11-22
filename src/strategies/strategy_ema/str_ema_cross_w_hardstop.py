from backtesting import Strategy
import src.indicators.i_ema as indicator

class ema_cross_w_hardstop_strategy(Strategy):
    #these emas doesnt count, im giving it as parameter to the strategy
    fast_ema_period = 0
    slow_ema_period = 0
    hardstop_percentage = 15
    cross_already_bought = False

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
        #check if position is already open
        if self.position:
            #close it if ema cross is bearish
            if fast_ema < slow_ema:
                print("CHIUSO POSIZIONE PER EMA CROSS")
                self.position.close()
        else:
             #open position if ema cross is bullish and 
             if fast_ema > slow_ema and not self.cross_already_bought:
                print("APRO POSIZIONE E ALREADY BUY A TRUE")
                self.cross_already_bought = True
                #buy with hardstop below a certain percetage
                stoploss = last_close - (last_close * self.hardstop_percentage/100)
                self.buy(size=0.01, sl= stoploss)
        #every bearish cross i set up that i can open position on the bullish cross
        if fast_ema < slow_ema:
            print("BEARISH CROSS QUINDI SETTO A FALSE ALREADY BUY")
            self.cross_already_bought = False

