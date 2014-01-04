# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import itertools as it
import numpy as np
import math
import copy


dt_start = dt.datetime(2008, 1, 1)
dt_end = dt.datetime(2009, 12, 31)
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

dataobj = da.DataAccess('Yahoo')
ls_symbols = dataobj.get_symbols_from_list('sp5002012')
ls_symbols.append('SPY')

ls_keys = ['close', 'open', 'actual_close']
ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))

for s_key in ls_keys:
    d_data[s_key] = d_data[s_key].fillna(method='ffill')
    d_data[s_key] = d_data[s_key].fillna(method='bfill')
    d_data[s_key] = d_data[s_key].fillna(1.0)

df_close = d_data['actual_close']
ts_market = df_close['SPY']

df_events = copy.deepcopy(df_close)
df_events = df_events * np.NAN

for i in range(1, len(ldt_timestamps)):
	for sym in ls_symbols:
		if df_close[sym].ix[ldt_timestamps[i]] < 8.0 and df_close[sym].ix[ldt_timestamps[i - 1]] >= 8.0:
			df_events[sym].ix[ldt_timestamps[i]] = 1
"""
events = 0
for i in range(1, 20):
	for sym in ls_symbols:
		if df_events[sym].ix[ldt_timestamps[i]] == 1:
			events += 1
for i in range(len(ldt_timestamps) - 20, len(ldt_timestamps)):
	for sym in ls_symbols:
		if df_events[sym].ix[ldt_timestamps[i]] == 1:
			events += 1

print "found", events, "events"
"""

ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='question3.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')







