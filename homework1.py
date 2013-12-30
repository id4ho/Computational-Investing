# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import itertools as it
import numpy as np


def simulate(dt_start, dt_end, ls_symbols, weights, first=False, verbose=False):

	answers = {'start': dt_start.strftime('%B %d, %Y'), 'end': dt_end.strftime('%B %d, %Y'), 'symbs': ls_symbols, 'allocations': weights}

	ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

	ls_keys = 'close'

	if first == True:
		dataobj = da.DataAccess('Yahoo', cachestalltime=0)
	else:
		dataobj = da.DataAccess('Yahoo')

	df_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
	
	# create a new DataFrame with normalized values (this will be how we apply the weights)
	normed_df = df_data / df_data.iloc[0]

	# apply the appropriate weight to every value in the DataFrame
	for i, symb in enumerate(ls_symbols):
		normed_df[symb] = normed_df[symb] * weights[i]

	# now that we've applied weights we can sum the values in the symbols columns to get a portfolio value
	normed_df['total'] = 0.0
	for i, symb in enumerate(ls_symbols):
		normed_df['total'] += normed_df[symb]
	
	normed_df['daily_rets'] = normed_df['total'].div(normed_df['total'].shift(), fill_value=1) - 1

	daily_rets = normed_df['daily_rets'].values

	answers['stdev'] = np.std(daily_rets)
	answers['cum_ret'] = (normed_df['total'][-1] / normed_df['total'][0])
	answers['average']  = np.mean(daily_rets)
	answers['sharpe'] = np.sqrt(252) * (answers['average']/answers['stdev'])

	if verbose:
		return """Start Date: {start}
End Date: {end}
Symbols: {symbs}
Optimal Allocations: {allocations}
Sharpe Ratio: {sharpe}
Volatility (stdev of daily returns):  {stdev}
Average Daily Return:  {average}
Cumulative Return:  {cum_ret}""".format(**answers)

	else: return answers


def hw1(start, end, symbols):
	for i, weights in enumerate(portfolio_weights(len(symbols), 10)):
		if i == 0: 
			best_sharpe = [simulate(start, end, symbols, weights, True)['sharpe'], weights]
		else:
			sharpe = simulate(start, end, symbols, weights)['sharpe']
			print (sharpe, weights)
			if sharpe > best_sharpe[0]:
				best_sharpe = [sharpe, weights]
	return best_sharpe

def portfolio_weights(num_symbols, increments=10):
	"""find all valid allocations with given increments and calculate the 
	best with respect to the supplied metric function"""

	if increments not in [1, 2, 4, 5, 10]:
		raise Exception("increment must be 1, 2, 4, 5, or 10!")
	
	i = 100.0
	allocations = [i/100.0]
	while i >= 0:
		allocations += [i/100.0]
		i -= increments
	print allocations

	valid_allocations = []
	for alloc in it.product(allocations, repeat = num_symbols):
		if sum(alloc) == 1.0:
			valid_allocations += [alloc]
	return valid_allocations


if __name__ == '__main__':
	print hw1(dt.datetime(2010, 1, 1), dt.datetime(2010, 12, 31), ['BRCM', 'ADBE', 'AMD', 'ADI'])

