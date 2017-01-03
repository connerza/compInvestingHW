import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import csv
import sys

if __name__ == '__main__':
	#Initial arguments -----------------------------------------------------------
	initialCash = int(sys.argv[1])
	inFileName = sys.argv[2]
	outFileName = sys.argv[3]

	#Read in trades --------------------------------------------------------------
	with open(inFileName, "rU") as csvFile:
		reader = csv.reader(csvFile, delimiter=",")
		trades = []
		for row in reader:
			tempDt = dt.datetime(int(row[0]), int(row[1]), int(row[2]), 16)
			row = row[3:]
			row.insert(0, tempDt)
			trades.append(row)

	#sort trades by date
	trades = sorted(trades, key=lambda x: x[0])
	#convert to ndarray
	trades = np.array(trades)
	#get list of symbols an remove duplicates
	ls_symbols = list(set(trades[:, 1]))
	#get list of dates, remove duplicates, and add 1 day
	ldt_dates = sorted(list(set(trades[:, 0])))
	startDate = ldt_dates[0]
	endDate = ldt_dates[-1] + dt.timedelta(days=1)
	ldt_timestamps = du.getNYSEdays(startDate, endDate, dt.timedelta(hours=16))

	#Get data ---------------------------------------------------------------------
	dataobj = da.DataAccess('Yahoo')
	data = dataobj.get_data(ldt_timestamps, ls_symbols, 'close')

	#Build data structures --------------------------------------------------------
	#build cash dataframe
	cash = [initialCash] * len(ldt_timestamps)
	cash = pd.DataFrame(cash, index=ldt_timestamps, columns=["cash"])
	#build holdings dataframe
	holdings = pd.DataFrame(index=ldt_timestamps, columns=ls_symbols)
	for sym in ls_symbols:
		holdings[sym] = holdings[sym].fillna(0)
	#build value dataframe
	value = pd.DataFrame(index=ldt_timestamps, columns=["value"])

	#Calculate values -------------------------------------------------------------
	for trade in trades:
		timestamp = trade[0]
		symbol = trade[1]
		numshares = int(trade[3])
		cashValueChange = data.ix[timestamp][symbol] * numshares
		if trade[2] == "Buy":
			cashValueChange = cashValueChange * -1
			holdingValueChange = numshares
		else:
			holdingValueChange = numshares * -1

		for j in range(ldt_timestamps.index(timestamp), len(ldt_timestamps)):
			cash.ix[ldt_timestamps[j]]['cash'] = cash.ix[ldt_timestamps[j]]['cash'] + cashValueChange
			holdings.ix[ldt_timestamps[j]][symbol] = holdings.ix[ldt_timestamps[j]][symbol] + holdingValueChange

	for timestamp in ldt_timestamps:
		holdingValue = 0
		for sym in ls_symbols:
			holdingValue = holdingValue + (holdings.ix[timestamp][sym] * data.ix[timestamp][sym])

		value.ix[timestamp]["value"] = cash.ix[timestamp]["cash"] + holdingValue

	with open(outFileName, 'wb') as csvFile:
		writer = csv.writer(csvFile, delimiter = ",")
		for timestamp in ldt_timestamps:
			row = [timestamp.date().year, timestamp.date().month, timestamp.date().day, int(value.ix[timestamp]['value'])]
			writer.writerow(row)
