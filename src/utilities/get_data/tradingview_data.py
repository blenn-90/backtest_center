#utility class used to import data from tradingview css files
import pandas as pd
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager

def append_row(df, row):
    return pd.concat([
                df, 
                pd.DataFrame([row], columns=row.index)]
           ).reset_index(drop=True)

def csv_to_dataframe(path, timeframe, filename, unit):
    #print("--> called csv_to_dataframe - path {}, timeframe {}, filename {}".format(
    #    path, timeframe, filename
    #))
    #reading csv file
    data = pd.read_csv(
        path + "\\" + timeframe + "\\" + filename,
        usecols=[0,1,2,3,4],
        names=["Date","Open","High","Low","Close"],
        skiprows=[0]
    )
    #print(data)
    #setting dataframe index
    data["Date"] = pd.to_datetime(data["Date"], unit=unit)
    data.set_index("Date", inplace=True)

    #print("--> ending csv_to_dataframe - path {}, timeframe {}, filename {}".format(
    #    path, timeframe, filename
    #))
    return data

def binance_csv_to_dataframe(path, timeframe, filename):
    return csv_to_dataframe(path, timeframe, filename, "ms")

def tradingview_csv_to_dataframe(path, timeframe, filename):
    return csv_to_dataframe(path, timeframe, filename, "s")