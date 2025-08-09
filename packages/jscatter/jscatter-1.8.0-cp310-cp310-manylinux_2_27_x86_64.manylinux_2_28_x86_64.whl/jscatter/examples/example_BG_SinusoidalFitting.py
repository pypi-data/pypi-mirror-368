# Basic fit examples with synthetic data. Usually data are loaded from a file.

import jscatter as js
import numpy as np

sinus = lambda x, A, a, B: A * np.sin(a * x) + B  # define model

# Fit sine to simulated data
x = np.r_[0:10:0.1]
data = js.dA(np.c_[x, np.sin(x) + 0.2 * np.random.randn(len(x)), x * 0 + 0.2].T)  # simulate data with error
data.fit(sinus, {'A': 1.2, 'a': 1.2, 'B': 0}, {}, {'x': 'X'})  # fit data
data.showlastErrPlot()  # show fit
data.errPlotTitle('Fit Sine')

# Fit sine to simulated data using an attribute in data with same name
data = js.dA(np.c_[x, 1.234 * np.sin(x) + 0.1 * np.random.randn(len(x)), x * 0 + 0.1].T)  # create data
data.A = 1.234  # add attribute
data.makeErrPlot()  # makes errorPlot prior to fit
data.fit(sinus, {'a': 1.2, 'B': 0}, {}, {'x': 'X'})  # fit using .A
data.errPlotTitle('Fit Sine with attribute')

# Fit sine to simulated data using an attribute in data with different name and fixed B
data = js.dA(np.c_[x, 1.234 * np.sin(x) + 0.1 * np.random.randn(len(x)), x * 0 + 0.1].T)  # create data
data.dd = 1.234  # add attribute
data.fit(sinus, {'a': 1.2, }, {'B': 0}, {'x': 'X', 'A': 'dd'})  # fit data
data.showlastErrPlot()  # show fit
data.errPlotTitle('Fit Sine with attribute and fixed B')

# Fit sine to simulated dataList using an attribute in data with different name
# and fixed B from data.
# first one common parameter then as parameter list
# create data
data = js.dL()
ef = 0.1  # increase this to increase error bars of final result
for ff in [0.001, 0.4, 0.8, 1.2, 1.6]:
    data.append(js.dA(np.c_[x, (1.234 + ff) * np.sin(x + ff) + ef * ff * np.random.randn(len(x)), x * 0 + ef * ff].T))
    data[-1].B = 0.2 * ff / 2  # add attributes

# fit with a single parameter for all data, obviously wrong result
data.fit(lambda x, A, a, B, p: A * np.sin(a * x + p) + B, {'a': 1.2, 'p': 0, 'A': 1.2}, {}, {'x': 'X'})
data.showlastErrPlot()  # show fit
data.errPlotTitle('Fit Sine with attribute and common fit parameter')

# now allowing multiple p,A,B as indicated by the list starting value
data.fit(lambda x, A, a, B, p: A * np.sin(a * x + p) + B, {'a': 1.2, 'p': [0], 'B': [0, 0.1], 'A': [1]}, {}, {'x': 'X'})
data.errPlotTitle('Fit Sine with attribute and non common fit parameter')

# plot p against A , just as demonstration
p = js.grace()
p.plot(data.A, data.p, data.p_err, sy=[1, 0.3, 1])
p.xaxis(label='Amplitude')
p.yaxis(label='phase')
