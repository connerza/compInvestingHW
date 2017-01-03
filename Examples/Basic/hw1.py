# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def simulate(startDate, endDate, symbols, allocations):
	#Read in adjusted closing prices for the 4 equities.
	dt_timeofday = dt.timedelta(hours = 16)
	ldt_timestamps = du.getNYSEdays(startDate, endDate, dt_timeofday)
	c_dataobject = da.DataAccess('Yahoo', cachestalltime=0)
	keys = ['close']
	ldf_data = c_dataobject.get_data(ldt_timestamps, symbols, keys)
	data = dict(zip(keys, ldf_data))

	# Filling the data for NAN
	for s_key in keys:
		data[s_key] = data[s_key].fillna(method='ffill')
		data[s_key] = data[s_key].fillna(method='bfill')
		data[s_key] = data[s_key].fillna(1.0)

	na_price = data['close'].values

	#Normalize the prices according to the first day. 
	#The first row for each stock should have a value of 1.0 at this point.
	na_price = na_price / na_price[0]

	#Multiply each column by the allocation to the corresponding equity.
	for i, equity in enumerate(symbols):
		na_price[:, i] = na_price[:, i] * allocations[i]

	#Sum each row for each day. That is your cumulative daily portfolio value.
	daily_rets = [sum(l)/sum(na_price[i-1]) - 1 for i,l in enumerate(na_price) if i != 0]
	daily_rets.insert(0, sum(na_price[0]) - 1)

	#Compute statistics from the total portfolio value.
	stdDevRet = np.std(daily_rets)
	avRet = sum(daily_rets) / len(daily_rets)
	sharpeRatio = np.sqrt(250) * avRet / stdDevRet
	cumRet = sum(daily_rets)
	return stdDevRet, avRet, sharpeRatio, cumRet

if __name__ == '__main__':
	optimal = {}
	optimal['sharpe'] = 0
	optimal['allocations'] = []

	startDate = dt.datetime(2010,1,1)
	endDate = dt.datetime(2010,12,31)
	symbols = ['BRCM', 'ADBE', 'AMD', 'ADI']

	for x in xrange(0,10):
		for y in xrange(0, 10-x):
			for z in xrange(0, 10-x-y):
				allocations = [x*.1, y*.1, z*.1, (10-x-y-z)*.1]
				stdDevRet, avRet, sharpeRatio, cumRet = simulate(startDate, endDate, symbols, allocations)
				if sharpeRatio > optimal['sharpe']:
					optimal['sharpe'] = sharpeRatio
					optimal['allocations'] = [x*.1, y*.1, z*.1, (10-x-y-z)*.1]
					optimal['volatility'] = stdDevRet
					optimal['average'] = avRet
					optimal['cumulative'] = cumRet

	print str.format("Start Date: {}", startDate.strftime("%B %d, %Y"))
	print str.format("End Date: {}", endDate.strftime("%B %d, %Y"))
	print str.format("Symbols: {}", symbols)
	print str.format("Optimal Allocations: {}", optimal['allocations'])
	print str.format("Sharpe Ratio: {}", optimal['sharpe'])
	print str.format("Volatility: {}", optimal['volatility'])
	print str.format("Average Daily Return: {}", optimal['average'])
	print str.format("Cumulative Return: {}", optimal['cumulative'])






