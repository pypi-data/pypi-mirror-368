
import jscatter as js
import numpy as np
from scipy.interpolate import LSQUnivariateSpline

# load data
ao50 = js.dA(js.examples.datapath + '/a0_336.dat')
ao50.conc = 50
ao10 = js.dA(js.examples.datapath + '/a0_338.dat')
ao10.conc = 2

p = js.grace(1.5, 1)
p.clear()

p.plot(ao50.X, ao50.Y, symbol=[1, 0.2, 9], legend='50 mg/ml')
p.plot(ao10.X, ao10.Y, line=0, symbol=[1, 0.05, 2], legend='2mg/ml')
p.xaxis(0, 6, label=r'Q / nm\S-1')
p.yaxis(0.05, 200, scale='logarithmic', label='I(Q) / a.u.')
p.title('smoothed X-ray data')
p.subtitle('inset is the extracted structure factor at low Q')

# smoothing with a spline
# determine the knots of the spline 
# less points than data points
t = np.r_[ao10.X[1]:ao10.X[-2]:30j]
# calculate the spline
f = LSQUnivariateSpline(ao10.X, ao10.Y, t)
# calculate the new y values of the spline at the x points
ys = f(ao10.X)
p.plot(ao10.X, ys, symbol=[1, 0.2, 5, 5], legend='2 mg/ml spline ')
p.plot(t, f(t), line=0, symbol=[1, 0.2, 2, 1], legend='knot of spline')

# other idea: use lower number of points with averages in intervals
# this makes 100 intervals with average X and Y values and errors if wanted. Check prune how to use it!
# this is the best solution and additionally creates good error estimate!!!
p.plot(ao10.prune(number=100), line=0, symbol=[1, 0.5, 4], legend='2mg/ml averaged')
p.legend(x=1, y=100, charsize=1.2)
p.xaxis(0, 6)
p.yaxis(0.05, 200, scale='logarithmic')

# make a smaller plot inside for the structure factor
p.new_graph()
p[1].SetView(0.6, 0.4, 0.9, 0.8)
p[1].plot(ao50.X, ao50.Y / ao10.Y, symbol=[1, 0.2, 1, ''], legend='structure factor')
p[1].yaxis(0.5, 1.3, label='S(Q)')
p[1].xaxis(0, 2, label=r'Q / nm\S-1')
p[1].legend(x=0.5, y=0.8)

p.save('smooth_xraydata.png')
