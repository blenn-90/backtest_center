import pandas_ta as ta

#ema calculator used in the strategies
def i_ema(data, ema_period):
    ema =  ta.ema(close = data.Close.s, length = ema_period)
    return ema.to_numpy().T
