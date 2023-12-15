import sys
import pandas as pd
import src.utilities.noshare_data as noshare_data
from kucoin.client import Client
import time
from datetime import datetime

def get_pairs():
    client = Client(noshare_data.kc_apikey, noshare_data.kc_secret, noshare_data.kc_passphrase)
    tickers = client.get_symbols()
    
    usdt_tickers = []
    for ticker in tickers:
        if 'USDT' in ticker['symbol'] and not ticker['symbol'].startswith('BUSD') and not ticker['symbol'].startswith('USD') and '3L-USDT' not in ticker['symbol'] and '3S-USDT' not in ticker['symbol']  and 'DOWN-USDT' not in ticker['symbol'] and 'UPUSDT' not in ticker['symbol'] and 'BEAR-USDT' not in ticker['symbol'] and 'BULL-USDT' not in ticker['symbol']  and not ticker['symbol'].startswith('TUSD') and not ticker['symbol'].startswith('EUR') and not ticker['symbol'].startswith('PAX'):
            usdt_tickers.append(ticker['symbol'])

    print(usdt_tickers)
    return usdt_tickers

def save_pair_data_4h(pair):
    client = Client(noshare_data.kc_apikey, noshare_data.kc_secret, noshare_data.kc_passphrase)
    interval = '4hour'
    years_2015_1_6 = [1420070400, 1433116800]
    years_2015_6_12 = [1433116800, 1451606400]
    years_2016_1_6 = [1451606400, 1464739200]
    years_2016_6_12 = [1464739200, 1483228800]
    years_2017_1_6 = [1483228800, 1496275200]
    years_2017_6_12 = [1496275200, 1514764800]
    years_2018_1_6 = [1514764800, 1527811200]
    years_2018_6_12 = [1527811200, 1546300800]
    years_2019_1_6 = [1546300800, 1559347200]
    years_2019_6_12 = [1559347200, 1577836800]
    years_2020_1_6 = [1577836800, 1590969600]
    years_2020_6_12 = [1590969600, 1609459200]
    years_2021_1_6 = [1609459200, 1622505600]
    years_2021_6_12 = [1622505600, 1640995200]
    years_2022_1_6 = [1640995200, 1654041600]
    years_2022_6_12 = [1654041600, 1672531200]
    years_2023_1_6 = [1672531200, 1685577600]
    years_2023_6_12 = [1685577600, 1704067200]
    years_2024_1_6 = [1704067200, 1717200000]

    all_years_divided_by_6_months = [years_2015_1_6, years_2015_6_12, years_2016_1_6, years_2016_6_12, years_2017_1_6, years_2017_6_12, years_2018_1_6, years_2018_6_12,
                                     years_2019_1_6, years_2019_6_12, years_2020_1_6, years_2020_6_12, years_2021_1_6, years_2021_6_12, years_2022_1_6, years_2022_6_12, 
                                     years_2023_1_6, years_2023_6_12, years_2024_1_6] 
    
    final_hist_df = pd.DataFrame(columns=['Date', 'Open', 'Close', 'High', 'Low'])
    final_hist_df.set_index("Date", inplace=True)
    numeric_columns = ['Open', 'High', 'Low', 'Close']
    final_hist_df[numeric_columns] = final_hist_df[numeric_columns].apply(pd.to_numeric, axis=1)

    for range_of_6_months in all_years_divided_by_6_months:
        
        historical = client.get_kline_data( pair, kline_type=interval, start=range_of_6_months[0], end=range_of_6_months[1])
        if not historical:
            print(pair + " no data between " +  str(datetime.fromtimestamp(range_of_6_months[0])) +" and " + str(datetime.fromtimestamp(range_of_6_months[1])))
        else:
            print(pair + " found data between " +  str(datetime.fromtimestamp(range_of_6_months[0])) +" and " + str(datetime.fromtimestamp(range_of_6_months[1])))
            hist_df = pd.DataFrame(historical)
            hist_df.columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Amount', 'Volume']
            hist_df['Date'] = pd.to_datetime(hist_df['Date'], unit='s')
            hist_df['Date']=hist_df['Date'].dt.round('15min')  
            hist_df.set_index("Date", inplace=True)
            hist_df = hist_df.drop(columns=['Amount','Volume'])
            numeric_columns = ['Open', 'High', 'Low', 'Close']
            hist_df[numeric_columns] = hist_df[numeric_columns].apply(pd.to_numeric, axis=1)
            #hist_df['Date'] = hist_df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
            final_hist_df = (final_hist_df.copy() if hist_df.empty else hist_df.copy() if final_hist_df.empty else pd.concat([final_hist_df, hist_df])) # if both DataFrames non empty)
    
    final_hist_df.sort_values(by='Date', inplace = True)
    final_hist_df.to_csv(sys.path[noshare_data.project_sys_path_position]+ "\\data\\kucoin_4h\\"+pair+".csv")
    return final_hist_df


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
save_all_usdt_pair_4h()
