# Fit sine to simulated dataList with a linked parameter
#
import jscatter as js
import numpy as np

# create data. B will appear several times with same value
data = js.dL()
x = np.r_[0:10:0.1]
ef = 0.1  # increase this to increase error bars of final result
for ff in [0.001, 0.8, 1.6]:
    data.append(js.dA(np.c_[x, (1.234 + ff) * np.sin(x + ff) + ef * ff * np.random.randn(len(x)), x * 0 + ef * ff].T))
    data[-1].B = 0.2 * ff / 2  # add attributes
    # add same but different amplitude A, same phase p
    data.append(js.dA(np.c_[x, (0.234 + ff) * np.sin(x + ff) + ef * ff * np.random.randn(len(x)), x * 0 + ef * ff].T))
    data[-1].B = 0.2 * ff / 2  # add attributes

data.append(js.dA(np.c_[x, (0.234 + ff) * np.sin(x + ff) + ef * ff * np.random.randn(len(x)), x * 0 + ef * ff].T))
data[-1].B = 0.2 * ff / 2  # add attributes


# create model
model = lambda x, A, a, B, p: A * np.sin(a * x + p) + B

# plot for result
p = js.grace()

# fit with independent parameters for all dataList elements
data.fit(model, {'a': 1.2, 'p': [0], 'A': [1.2]}, {}, {'x': 'X'})

# plot p against unique B
p.plot(data.B, data.p, data.p_err, sy=[1, 1, 1], legend='independent p with 7 values')

# now A still independent but we link 'p' to 'B'
data.fit(model, {'a': 1.2, 'p': [0, 'B'], 'A': [1]}, {}, {'x': 'X'})

# plot p against unique B with less values in p
p.plot(data.B.unique, data.p, data.p_err, sy=[2, 0.7, 4], le='linked p with 3 values')
p.xaxis(label='B', min=-0.1, max=0.25)
p.yaxis(label='phase',min=-0.5,max=2.5)
p.legend(x=-0.05,y=2)
p.save('SinusoidalFit_linkedParameter.png')

