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
import csv, sys

csv_values = csv.reader(open(sys.argv[1], 'rU'), delimiter=',')

dates = []
values = []
results = {}

for row in csv_values:
	dates.append(dt.datetime(int(row[0]),int(row[1]),int(row[2])))
	values.append(float(str(row[3])))
	results['final_value'] = row[0], row[1], row[2], row[3]

#create the DataFrame object with portfolio's value from the input csv
port_values = pd.DataFrame({'portfolio' : pd.Series(values, index=dates)})


#pull all the benchmark data from QSTK for comparison
dt_start = dates[0]
dt_end = dates[-1]
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
ls_keys = 'close'
ls_symbs = [sys.argv[2]]
dataobj = da.DataAccess('Yahoo')
benchmark_data = dataobj.get_data(ldt_timestamps, ls_symbs, ls_keys)

benchmark_data.index = benchmark_data.index - dt.timedelta(hours=16) #need to make index match port_values

#create normalized returns to get total return and to normalize the benchmark
port_values['return_port'] = port_values['portfolio'].div(port_values['portfolio'].loc[0])
port_values['return_benchmark'] = benchmark_data[sys.argv[2]].div(benchmark_data[sys.argv[2]].loc[0])
port_values['norm_bench'] = port_values['return_benchmark'] * port_values['portfolio'].loc[0]

port_values['daily_port'] = port_values['portfolio'].div(port_values['portfolio'].shift()) - 1
port_values['daily_port'].loc[0] = 0

port_values['daily_bench'] = benchmark_data[sys.argv[2]].div(benchmark_data[sys.argv[2]].shift()) - 1
port_values['daily_bench'].loc[0] = 0

results['begin'] = dt_start
results['end'] = dt_end
results['ret_port'] = port_values['return_port'].loc[-1]
results['ret_bench'] = port_values['return_benchmark'].loc[-1]
results['dev_port'] = np.std(port_values['daily_port'].values)
results['dev_bench'] = np.std(port_values['daily_bench'].values)
results['daily_port'] = np.mean(port_values['daily_port'].values)
results['daily_bench'] = np.mean(port_values['daily_bench'].values)
results['sharpe_port'] = np.sqrt(252) * (results['daily_port']/results['dev_port'])
results['sharpe_bench'] = np.sqrt(252) * (results['daily_bench']/results['dev_bench'])

plt.clf()
plt.plot(port_values.index, port_values['portfolio'])
plt.plot(port_values.index, port_values['norm_bench'])
plt.legend(['portfolio', 'benchmark'], 'lower left')
plt.ylabel('Adjusted Close')
plt.xlabel('Date')
plt.savefig('hw2.pdf', format='pdf')


print """
The final value of the portfolio using the sample file is -- {final_value}

Details of the Performance of the portfolio :

Data Range :  {begin}  to  {end}

Sharpe Ratio of Fund : {sharpe_port}
Sharpe Ratio of $SPX : {sharpe_bench}

Total Return of Fund :  {ret_port}
Total Return of $SPX : {ret_bench}

Standard Deviation of Fund :  {dev_port}
Standard Deviation of $SPX : {dev_bench}

Average Daily Return of Fund :  {daily_port}
Average Daily Return of $SPX : {daily_bench}""".format(**results)





