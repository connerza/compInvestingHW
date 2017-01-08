import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import csv
import sys
import matplotlib.pyplot as plt

class TrendStatistics(object):
    """"""
    def __init__(self, name, startDate, endDate, statistics):
        super(TrendStatistics, self).__init__()
        self.stdDevRet = statistics[0]
        self.avRet = statistics[1]
        self.sharpeRatio = statistics[2]
        self.cumRet = statistics[3]
        self.normalizedValues = statistics[4]
        self.name = name
        self.startDate = startDate
        self.endDate = endDate

    def printStatistics(self):
        print "Performance details for " + self.name + "\n"
        print "Date Range: " + str(self.startDate) + " - " + str(self.endDate)
        print "Sharpe Ratio: " + str(self.sharpeRatio)
        print "Cumulative Return: " + str(self.cumRet)
        print "Std Deviation: " + str(self.stdDevRet)
        print "Av Daily Return" + str(self.avRet) + "\n"

def calcStatistics(values):
    """Tobe used in conjunction with TrendStatistics (feed into contructor)"""
    #Normalize the values according to the first day. 
    normalizedValues = values / values[0]

    #Calculate daily return
    daily_rets = [l/normalizedValues[i-1] - 1 for i,l in enumerate(normalizedValues) if i != 0]
    daily_rets.insert(0, normalizedValues[0] - 1)

    #Compute statistics from the total portfolio value.
    stdDevRet = np.std(daily_rets)
    avRet = sum(daily_rets) / len(daily_rets)
    sharpeRatio = np.sqrt(250) * avRet / stdDevRet
    cumRet = normalizedValues[-1] - normalizedValues[0] / normalizedValues[0] + 1
    return stdDevRet, avRet, sharpeRatio, cumRet, normalizedValues

if __name__ == '__main__':
    infilename = sys.argv[1]
    compareSym = sys.argv[2]

    with open(infilename, 'rU') as file:
        reader = csv.reader(file, delimiter=",")
        timestamps = []
        values = []
        for row in reader:
            timestamps.append(dt.datetime(int(row[0]), int(row[1]), int(row[2]), 16))
            values.append(float(row[3]))
        values = np.array(values)

    #Get data for reference symbol
    dataObject = da.DataAccess('Yahoo')
    refData = dataObject.get_data(timestamps, [compareSym], 'close')
    refData[compareSym].fillna(method='ffill')
    refData[compareSym].fillna(method='bfill')
    refData[compareSym].fillna(1.0)

    #Calculating statistics ----------------------------------------------------------
    portfolioStatistics = TrendStatistics("Portfolio", timestamps[0], timestamps[-1], calcStatistics(values))
    refStatistics = TrendStatistics(compareSym, timestamps[0], timestamps[-1], calcStatistics(refData[compareSym]))

    #Plotting normalized value -------------------------------------------------------------------------
    plt.clf()
    plt.plot(timestamps, portfolioStatistics.normalizedValues)  # portfolio values
    plt.plot(timestamps, refStatistics.normalizedValues) # ref values
    plt.axhline(y=0, color='r')
    plt.legend(['Portfolio', compareSym], loc=3)
    plt.ylabel('Adjusted Close')
    plt.xlabel('Date')
    plt.savefig('values.pdf', format='pdf')

    portfolioStatistics.printStatistics()
    refStatistics.printStatistics()