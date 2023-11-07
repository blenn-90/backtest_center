import pandas as pd
apikey = '8K4vWPeslbsn84btWqk6Skb8gLvvr9naLoE8cZ05sBUfcWhYoAvoPKjafoDTlvkV'
secret = 'SrIICejyibgYV44F4pIvN4zdPHvZ9NezmHJf3kh2Rntte3ToZ3j4GaNhR233ZS6C'
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager

def get_binance_data():
    client = Client(apikey, secret)
    
    historical = client.get_historical_klines('ETHUSDT', Client.KLINE_INTERVAL_1DAY, '1 Jan 2011')
    hist_df = pd.DataFrame(historical)
    hist_df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 
                    'Number of Trades', 'TB Base Volume', 'TB Quote Volume', 'Ignore']
    hist_df['Date'] = pd.to_datetime(hist_df['Date']/1000, unit='s')
    hist_df.set_index("Date", inplace=True)
    hist_df = hist_df.drop(columns=['Volume', 'Close Time', 'Quote Asset Volume', 'Number of Trades', 'TB Base Volume', 'TB Quote Volume', 'Ignore'])
    numeric_columns = ['Open', 'High', 'Low', 'Close']
    hist_df[numeric_columns] = hist_df[numeric_columns].apply(pd.to_numeric, axis=1)
    
    print(hist_df.dtypes)
    hist_df.to_csv()
    return(hist_df)

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