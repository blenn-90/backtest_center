import pandas_ta as ta
import pandas as pd
import numpy as np
from scipy.stats import linregress
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime


def i_flag(data):
    df_final = pd.DataFrame(data.index, columns=["datetime"])
    df_final.set_index('datetime', inplace = True)
    
    df = pd.DataFrame(data.index, columns=["datetime"])
    df.set_index('datetime', inplace = True)
    df['Open'] = data.Open
    df['Close'] = data.Close
    df['High'] = data.High
    df['Low'] = data.Low
    df['pivot'] = df.apply(lambda x: pivotid(df, x.name,3,3), axis=1)
    #df['pointpos'] = df.apply(lambda row: pointpos(row), axis=1)
    #df['flag'] = df.index.map(lambda x: detect_flag(df, x, 35, 3))
    #df[df['flag']!=0]
    
    df_final = df[['pivot']].copy()
    print(df_final)
    return df_final.to_numpy().T

def pivotid(df1, l, n1, n2): #n1 n2 before and after candle l
    if l-n1 < 0 or l+n2 >= len(df1):
        return 0
    
    pividlow=1
    pividhigh=1
    for i in range(l-n1, l+n2+1):
        if(df1.Low[l]>df1.Low[i]):
            pividlow=0
        if(df1.High[l]<df1.High[i]):
            pividhigh=0
    if pividlow and pividhigh:
        return 3
    elif pividlow:
        return 1
    elif pividhigh:
        return 2
    else:
        return 0
    

def pointpos(x):
    if x['pivot']==1:
        return x['Low']-1e-3
    elif x['pivot']==2:
        return x['High']+1e-3
    else:
        return np.nan


def detect_flag(df, candle, backcandles, window, plot_flag=False):
    """
    Attention! window should always be greater than the pivot window! to avoid look ahead bias
    """
    localdf = df[candle-backcandles-window:candle-window]  
    highs = localdf[localdf['pivot'] == 2].High.tail(3).values
    idxhighs = localdf[localdf['pivot'] == 2].High.tail(3).index
    lows = localdf[localdf['pivot'] == 1].Low.tail(3).values
    idxlows = localdf[localdf['pivot'] == 1].Low.tail(3).index

    if len(highs) == 3 and len(lows) == 3:
        order_condition = ( 
            (idxlows[0] < idxhighs[0] 
            < idxlows[1] < idxhighs[1] 
            < idxlows[2] < idxhighs[2]) 
            or 
            (idxhighs[0] < idxlows[0] 
             < idxhighs[1] < idxlows[1] 
             < idxhighs[2] < idxlows[2]) )
        
        slmin, intercmin, rmin, _, _ = linregress(idxlows, lows)
        slmax, intercmax, rmax, _, _ = linregress(idxhighs, highs)

        if (order_condition 
            and (rmax*rmax)>=0.9 
            and (rmin*rmin)>=0.9 
            and slmin>=0.0001 
            and slmax<=-0.0001):
            #and ((abs(slmin)-abs(slmax))/abs(slmax)) < 0.05):

            if plot_flag:
                fig = go.Figure(data=[go.Candlestick(x=localdf.index,
                open=localdf['Open'],
                high=localdf['High'],
                low=localdf['Low'],
                close=localdf['Close'])])

                fig.add_scatter(x=localdf.index, y=localdf['pointpos'], mode="markers",
                marker=dict(size=10, color="MediumPurple"),
                name="pivot")
                fig.add_trace(go.Scatter(x=idxlows, y=slmin*idxlows + intercmin, mode='lines', name='min slope'))
                fig.add_trace(go.Scatter(x=idxhighs, y=slmax*idxhighs + intercmax, mode='lines', name='max slope'))
                fig.update_layout(
                xaxis_rangeslider_visible=False,
                plot_bgcolor='white', # change the background to white
                xaxis=dict(showgrid=True, gridcolor='white'), # change the x-axis grid to white
                yaxis=dict(showgrid=True, gridcolor='white') # change the y-axis grid to white
                )
                fig.show()

            return 1
    
    return 0

