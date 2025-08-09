# import jscatter and numpy
import numpy as np
import jscatter as js

# read the data (16 dataArrays) with attributes as q, Dtrans .... into dataList
i5 = js.dL(js.examples.datapath + '/iqt_1hho.dat')

# define a model for the fit
diffusion = lambda A, D, t, wavevector, e=0: A*np.exp(-wavevector**2*D*t) + e

# do the fit
# single valued start parameters are the same for all 16 dataArrays
# list start parameters [...] indicate independent fitting for dataArrays
# the command line shows progress and the final result, which is found in i5.lastfit
i5.fit(model=diffusion,                         # the fit function
       freepar={'D': [0.08], 'A': 0.98},        # free start parameters
       fixpar={'e': 0.0},                       # fixed parameters
       mapNames={'t': 'X', 'wavevector': 'q'})  # map names from model to data

# open plot with results and residuals
i5.showlastErrPlot(yscale='l')

# open a plot with fixed size and plot data and fit result
p = js.grace(1.2, 0.8)
# plot the data with Q values in legend as symbols
p.plot(i5, symbol=[-1, 0.4, -1], legend='Q=$q')
# plot fit results in lastfit as lines without symbol or legend
p.plot(i5.lastfit, symbol=0, line=[1, 1, -1])
# extend to longer times by changing a model parameter (points)
p.plot(i5.modelValues(t=np.r_[10:120:5]), symbol=0, line=[2, 1, -1])

# pretty up if needed
p.yaxis(min=0.02, max=1.1, scale='log', charsize=1.5, label='I(Q,t)/I(Q,0)')
p.xaxis(min=0, max=130, charsize=1.5, label='t / ns')
p.legend(x=110, y=0.9, charsize=1)
p.title('I(Q,t) as measured by Neutron Spinecho Spectroscopy', size=1.3)
p.text('for diffusion a single exp. decay', x=60, y=0.35, rot=360 - 20, color=4)
p.text(r'f(t)=A*e\S-Q\S2\N\SDt', x=100, y=0.025, rot=0, charsize=1.5)

if 1:  # optional; save in different formats
    p.save('DiffusionFit.agr')
    p.save('DiffusionFit.png')

# This is the basis of the simulated data above
D = js.dA(js.examples.datapath + '/1hho.Dq')

# Plot the result in an additional plot
p1 = js.grace(1, 1)  # plot with a defined size
p1.plot(i5.q, i5.D, i5.D_err, symbol=[2, 1, 1, ''], legend='average effective D')
p1.plot(D.X, D.Y * 1000., sy=0, li=1, legend='diffusion coefficient 1hho')
# pretty up if needed
p1.title('diffusion constant of a dilute protein in solution', size=1.5)
p1.subtitle('the increase is due to rotational diffusion on top of translational diffusion at Q=0', size=1)
p1.xaxis(min=0, max=3, charsize=1.5, label=r'Q / nm\S-1')  # xaxis numbers in size 1.5
p1.yaxis(min=0.05, max=0.15, charsize=1.5, label=r'D\seff\N / nm\S2\N/ns')
p1.legend(x=1, y=0.14)

if 1:
    p1.save('effectiveDiffusion.agr')
    p1.save('effectiveDiffusion.png')
