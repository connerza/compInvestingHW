# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep


# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import copy
import math

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""
def find_events(ls_symbols, df_bollinger):
    # Creating an empty dataframe
    df_events = copy.deepcopy(df_bollinger)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_bollinger.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Get applicable bollinger values
            bollToday = df_bollinger[s_sym].ix[ldt_timestamps[i]]
            bollYesterday = df_bollinger[s_sym].ix[ldt_timestamps[i - 1]]
            bollMarket = df_bollinger['SPY'].ix[ldt_timestamps[i]]

            # Event is found if 
                # boll today is <= -2 and
                # boll yesterday >= -2 and
                # boll of market >= 1
            if bollToday <= -2.0 and bollYesterday >= -2.0 and bollMarket >= 1.0:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events

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
    #Get data
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')
    ls_keys = ['close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    print "Finding Bollinger Values"
    mean, std, bollinger = calcBollinger(d_data['close'], 20)

    print "Finding Events"
    df_events = find_events(ls_symbols, bollinger)

    print "Profiling Events"
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
        s_filename='MyEventStudy.pdf', b_market_neutral=True, b_errorbars=True,
        s_market_sym='SPY')

    
