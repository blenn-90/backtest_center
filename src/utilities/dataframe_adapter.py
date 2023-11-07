#https://github.com/StreamAlpha/tvdatafeed to Dataframe
def dataframe_adapter(df):
    print("--> called dataframe_adapter - path {df}".format(
        df
    ))
    df2 = df.rename({'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, axis='columns')
    df3 = df2.drop('symbol', axis=1)
    print("--> ending dataframe_adapter - path {df}".format(
        df
    ))
    return df3