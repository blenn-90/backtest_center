import itertools

#use this object to save all the data get from different exchanges
class PairData:
    #object it represents the result of a strategy backtested  
    def __init__(self, pair, filename, source, data, isFirstCycle):
        self.pair = pair
        self.filename = filename
        self.source = source
        self.data = data
        self.isFirstCycle = isFirstCycle

def create_pair_data(pair, filename, source, data, isFirstCycle):
    return PairData(
            pair, 
            filename,
            source,
            data,
            isFirstCycle)

def getListNoDuplicate(list_pair_data):
    final_list_pair_data = {}
    for pair_data in list_pair_data:
        if pair_data.pair in list(final_list_pair_data.keys()):
            if str(pair_data.source) == "binance":
                continue
        final_list_pair_data[pair_data.pair] = pair_data

    
    return final_list_pair_data