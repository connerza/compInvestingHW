# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def calcBollinger(df_data, lBack):
    """Takes in a pandas df with columns as symbols and vals representing those symbol close values
        Outputs 3 dataframes: rollingMean, rollingStd, bollingerVals"""
    df_rollingMean = pd.DataFrame(index = df_data.index)
    df_rollingStd = pd.DataFrame(index = df_data.index)
    df_bollinger = pd.DataFrame(index = df_data.index)
    for sym in df_data.columns:
        rollingSeries = df_data[sym].rolling(window = lBack, center = False)
        df_rollingMean[sym] = rollingSeries.mean()
        df_rollingStd[sym] = rollingSeries.std()
        tempSeries = pd.Series(index = df_data.index)
        for t in df_data.index:
            tempSeries.ix[t] = (df_data.ix[t][sym] - df_rollingMean.ix[t][sym]) / df_rollingStd.ix[t][sym]
        df_bollinger[sym] = tempSeries

    return df_rollingMean, df_rollingStd, df_bollinger

if __name__ == '__main__':
    #Get data ---------------------------------------------------------------------
    dt_start = dt.datetime(2010, 1, 1)
    dt_end = dt.datetime(2010, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo')
    data = dataobj.get_data(ldt_timestamps, ['AAPL','GOOG','IBM','MSFT'], 'close')
    mean, std, bollinger = calcBollinger(data, 20)
    print bollinger
