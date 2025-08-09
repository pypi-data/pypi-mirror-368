import numpy as np
import jscatter as js

# create a stacked chart of 10 plots

# create some data
mean = 5
x = np.r_[mean - 3 * 3:mean + 3 * 3:200j]
data = js.dL()  # empty dataList
for sigma in np.r_[3:0.3:10j]:
    temp = js.dA(np.c_[x, np.exp(-0.5 * (x - mean) ** 2 / sigma ** 2) / sigma / np.sqrt(2 * np.pi)].T)
    temp.sigma = sigma
    data.append(temp)

p = js.grace()
# each shifted by hshift,vshift
# the yaxis is switched off for all except the first
p.stacked(10, hshift=0.02, vshift=0.01, yaxis='off')
# plot some Gaussians in each graph
for i, dat in enumerate(data):
    p[i].plot(dat, li=[1, 2, i + 1], sy=0, legend='sigma=$sigma')
# choose the same yscale for the data but no ticks for the later plots
# adjusting the scale and the size of the xaxis ticks

p[0].yaxis(min=0, max=1, tick=[0.2, 5, 0.3, 0.1])
p[0].xaxis(min=min(x), max=max(x), tick=[1, 1, 0.3, 0.1])
for pp in p.g[1:]:
    pp.yaxis(min=0, max=1, tick=False)
    pp.xaxis(min=min(x), max=max(x), tick=[1, 1, 0.3, 0.1])

# This plot is shown below; no fine tuning
if 1:
    p.save('stackedGaussians.agr')
    p.save('stackedGaussians', format='jpeg')

# change the stacking to improve plot (or not)
p.stacked(10, hshift=-0.015, vshift=-0.01, yaxis='off')
p.title('stacked')
# create a plot with exponential decaying function but shifted consecutively by factors of 2
x = js.loglist(0.01, 5, 100)
p = js.grace()
for i in np.r_[1:10]:
    p.plot(x, np.exp(-i ** 2 * x ** 2))

p.shiftbyfactor(xfactors=2 * np.r_[10:1:-1], yfactors=2 * np.r_[10:1:-1])
p.yaxis(scale='l')
p.xaxis(scale='l')
