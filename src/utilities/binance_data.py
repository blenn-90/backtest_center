import pandas as pd
apikey = '8K4vWPeslbsn84btWqk6Skb8gLvvr9naLoE8cZ05sBUfcWhYoAvoPKjafoDTlvkV'
secret = 'SrIICejyibgYV44F4pIvN4zdPHvZ9NezmHJf3kh2Rntte3ToZ3j4GaNhR233ZS6C'
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager


def get_pairs():
    client = Client(apikey, secret)
    tickers = client.get_all_tickers()
    usdt_tickers = []
    for ticker in tickers:
        if 'USDT' in ticker['symbol'] and not ticker['symbol'].startswith('USDT') and 'DOWNUSDT' not in ticker['symbol'] and 'UPUSDT' not in ticker['symbol']:
            usdt_tickers.append(ticker['symbol'])

    return usdt_tickers

def save_pair_data_1d(pair):
    client = Client(apikey, secret)
    interval = Client.KLINE_INTERVAL_1DAY

    historical = client.get_historical_klines(pair, interval, '1 Jan 2011')
    hist_df = pd.DataFrame(historical)
    hist_df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 
                    'Number of Trades', 'TB Base Volume', 'TB Quote Volume', 'Ignore']
    hist_df['Date'] = pd.to_datetime(hist_df['Date']/1000, unit='s')
    hist_df.set_index("Date", inplace=True)
    hist_df = hist_df.drop(columns=['Volume', 'Close Time', 'Quote Asset Volume', 'Number of Trades', 'TB Base Volume', 'TB Quote Volume', 'Ignore'])
    numeric_columns = ['Open', 'High', 'Low', 'Close']
    hist_df[numeric_columns] = hist_df[numeric_columns].apply(pd.to_numeric, axis=1)
    hist_df.to_csv("c:\\Users\\Alessandro\\Desktop\\python\\backtest_center_v2\\data\\binance_1d\\"+pair+".csv")
    return(hist_df)

def save_pair_data_4h(pair):
    client = Client(apikey, secret)
    interval = Client.KLINE_INTERVAL_4HOUR

    historical = client.get_historical_klines(pair, interval, '1 Jan 2011')
    print(historical)
    hist_df = pd.DataFrame(historical)
    hist_df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 
                    'Number of Trades', 'TB Base Volume', 'TB Quote Volume', 'Ignore']
    hist_df['Date'] = pd.to_datetime(hist_df['Date']/1000, unit='s')
    hist_df.set_index("Date", inplace=True)
    hist_df = hist_df.drop(columns=['Volume', 'Close Time', 'Quote Asset Volume', 'Number of Trades', 'TB Base Volume', 'TB Quote Volume', 'Ignore'])
    numeric_columns = ['Open', 'High', 'Low', 'Close']
    hist_df[numeric_columns] = hist_df[numeric_columns].apply(pd.to_numeric, axis=1)
    print(hist_df)
    hist_df.to_csv("c:\\Users\\Alessandro\\Desktop\\python\\backtest_center_v2\\data\\binance_4h\\"+pair+".csv")
    return(hist_df)


def save_all_usdt_pair_1d():
    usdt_tickers = get_pairs()
    for usdt_ticker in usdt_tickers:
        save_pair_data_1d(usdt_ticker)

def save_all_usdt_pair_4h():
    usdt_tickers = get_pairs()
    for usdt_ticker in usdt_tickers:
        save_pair_data_4h(usdt_ticker)

def read_csv_data(path, timeframe, filename):
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
    data["Date"] = pd.to_datetime(data["Date"])
    data.set_index("Date", inplace=True)

    #print("--> ending csv_to_dataframe - path {}, timeframe {}, filename {}".format(
    #    path, timeframe, filename
    #))
    return data

#save_all_usdt_pair_1d()
#save_all_usdt_pair_4h()