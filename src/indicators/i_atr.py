import pandas_ta as ta

#ema calculator used in the strategies
def i_atr(data, length):
    atr = ta.atr(data.High.s, data.Low.s, data.Close.s, length=length)
    return atr.to_numpy().T
