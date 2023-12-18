#utility class used to import data from tradingview css files
import pandas as pd
import sys
import src.utilities.noshare_data as noshare_data 
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from os import listdir
from os.path import isfile, join
from pathlib import Path
import src.classes.pair_data as pair_data

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

def read_csv_data(path, timeframe, filename):
    return csv_to_dataframe(path, timeframe, filename, "s")

def get_file_data_set():
    path = sys.path[noshare_data.project_sys_path_position] + "\\data"
    # retrive all in-sample tradingview files
    folder_tradingview = "tradingview_4h"
    print("checking files from {folder} folder".format( folder = folder_tradingview ))
    tradingview_data_file_set_is = [f for f in listdir(path + "\\" + folder_tradingview) if isfile(join(path + "\\" + folder_tradingview, f))]
    print ("found " + str(len(tradingview_data_file_set_is)) + " pairs")
    return tradingview_data_file_set_is

def get_insample_list(tradingview_data_file_set_is, path, folder_tradingview):
    insample_list = {}
    for data_file in tradingview_data_file_set_is:
        #importing tradinview insample files
        data = read_csv_data(path, folder_tradingview, data_file)
        pairdata = pair_data.create_pair_data(Path(data_file).stem, data_file, "tradingview", data, True)
        insample_list[pairdata.pair] = pairdata
    
    return insample_list

