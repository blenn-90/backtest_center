from backtesting import Strategy
import src.indicators.i_ema as indicator_ema
import src.indicators.i_atr as indicator_atr
import src.strategies.sources as sources

class ema_cross_w_atr_strategy(Strategy):
    #these emas doesnt count, im giving it as parameter to the strategy
    fast_ema_period = 0
    slow_ema_period = 0
    hardstop_opt = 0
    special_exit_opt = 0
    atr_length = sources.atr_length
    cross_already_bought = True

    def init(self):

        #calculate fast and slow ema matrix
        self.fast_ema_indicator = self.I(indicator_ema.i_ema, self.data, ema_period = self.fast_ema_period, overlay=True, plot=True)
        self.slow_ema_indicator = self.I(indicator_ema.i_ema, self.data, ema_period = self.slow_ema_period, overlay=True, plot=True)
        self.atr = self.I(indicator_atr.i_atr, self.data, length = self.atr_length)

    def next(self):
        #get last fast and slow ema from indicator
        fast_ema = self.fast_ema_indicator[-1]
        slow_ema = self.slow_ema_indicator[-1]
        #get last close value
        last_close = self.data.Close[-1]
        #atr percentuale
        atr_perc = self.atr[-1] / self.data.Close[-1] * 100
        #setting hardstop
        hardstop_final = atr_perc * self.hardstop_opt
        stoploss = last_close - (last_close * hardstop_final / 100)
        if stoploss < 0:
            stoploss = 0
        
        #check if position is already open
        if self.position:
            #close it if ema cross is bearish
            if fast_ema < slow_ema or self.special_exit_opt * slow_ema < last_close:
                self.position.close()
        else:
             #open position if ema cross is bullish and 
             if fast_ema > slow_ema and not self.cross_already_bought:
                self.cross_already_bought = True
                #buy with hardstop below a certain percetage
                
                self.buy(size=0.01, sl = stoploss)

        #every bearish cross i set up that i can open position on the bullish cross
        if fast_ema < slow_ema:
            self.cross_already_bought = False

