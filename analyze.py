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
import csv, sys, copy

orders = csv.reader(open(sys.argv[2], 'rU'), delimiter=',')

dates = []
symbs = []

for row in orders:
	dates.append(dt.datetime(int(row[0]),int(row[1]),int(row[2])))
	symbs.append(str(row[3]))

ls_symbols = list(set(symbs))
ls_symbols.append('SPY')

dates = list(set(dates))
dates.sort()
dt_start = dates[0]
dt_end = dates[-1]
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

ls_keys = ['close', 'open', 'actual_close']

dataobj = da.DataAccess('Yahoo')
ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))

for s_key in ls_keys:
    d_data[s_key] = d_data[s_key].fillna(method='ffill')
    d_data[s_key] = d_data[s_key].fillna(method='bfill')
    d_data[s_key] = d_data[s_key].fillna(1.0)

df_close = d_data['close']
ts_market = df_close['SPY']

stocks = pd.DataFrame(index=df_close.index, columns=df_close.columns)
stocks = stocks.fillna(0.0) # current ownership of stocks
trades = copy.deepcopy(stocks) # movements of stocks

#action equivalent affect on cash..
action = {'buy':-1, 'sell':1}

unordered_trades = []
for row in csv.reader(open(sys.argv[2], 'rU'), delimiter=','):
	trade_date = dt.datetime(int(row[0]), int(row[1]), int(row[2])) + dt.timedelta(hours=16)
	c_flow = action[str(row[4]).lower()]
	stock_flow = c_flow * -1 #cash outflow (i.e. negative 1) is a stock inflow
	unordered_trades.append((trade_date, str(row[3]), c_flow, stock_flow, int(row[5])))

ordered_trades = sorted(unordered_trades)

for trade in ordered_trades:
	trade_date, symb, c_flow, stock_flow, share_num = trade
	
	trades[symb][trade_date] += c_flow * share_num
	
	if not trade_date == ldt_timestamps[0] and stocks[symb][trade_date] == 0:
		symb_holdings = stocks[symb][ldt_timestamps[ldt_timestamps.index(trade_date) - 1]] + (stock_flow * share_num)
	else:
		symb_holdings = stocks[symb][trade_date] + (stock_flow * share_num)
	stocks[symb][trade_date:] = symb_holdings

portfolio = stocks * df_close
cash_flow = trades * df_close

portfolio['stock_value'] = portfolio.sum(axis=1)
portfolio['cashflows'] = cash_flow.sum(axis=1)
portfolio['cash'] = 0

for i, date in enumerate(portfolio.index):
	flow = portfolio['cashflows'][date]
	if i == 0:
		portfolio['cash'].iloc[i] = int(sys.argv[1]) + flow
	else:
		portfolio['cash'].iloc[i] = portfolio['cash'].iloc[i - 1] + flow

portfolio['port_value'] = portfolio['stock_value'] + portfolio['cash']
print portfolio.to_string()

writer = csv.writer(open(sys.argv[3], 'w'), delimiter=',')
for row_index in portfolio.index:
	ds = row_index.strftime("%Y %m %d")
	pv = portfolio['port_value'][row_index]
	row_to_enter = ds.split() + [pv]
	writer.writerow(row_to_enter)





