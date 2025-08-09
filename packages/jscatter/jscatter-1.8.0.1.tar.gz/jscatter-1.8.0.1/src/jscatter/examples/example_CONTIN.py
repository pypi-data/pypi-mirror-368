# -*- coding: utf-8 -*-
import numpy as np
import scipy.integrate.trapezoid as trapz
import jscatter as js

# read the data from Zetasizer exported data
# the wrapper takes the content from the header line which is consistent with the first data line
alldls = js.dls.readZetasizerNano(js.examples.datapath + '/dlsPolymerSolution.txt', NANOlocale=['de_DE', 'UTF-8'])
# we select one sample
# .X,.Y contain the correlation data
dls = alldls[4]

p = js.grace()
p.title('CONTIN analysis of DLS data')
p.multi(2, 1)
p[0].plot(dls, legend='correlation data')
p[0].plot(dls.distributions.X, dls.distributions.Y / 20, li=1, legend='relax. time intensity weighted')
p[1].plot(dls.distributions[1], dls.distributions[2] / 20, li=1, legend='radius intensity weighted')
# p[2].plot(dls.distributions[0],dls.distributions[2]/1000,li=1,legend='radius time intensity weighted')

p[0].xaxis(scale='l', label=r'correlation time / µs ', tick=[10, 9])
p[1].xaxis(scale='l', label=r'radius / nm ', tick=[10, 9])
# p[2].xaxis(scale='l',label=r'time / micros ',tick=[10,9])

# do the contin with the .X .Y data as intensity weighted relaxation time
resx = js.dls.contin(dls, a=173, tmin=1, tmax=1e5, typ=0, bgr=0.05, distribution='x', T=(273 + dls.Temperature))
p[0].plot(resx[0].contin_result_fit, li=4, sy=0, legend='contin result fit relaxation time')
p[0].plot(resx[0].contin_bestFit.X, resx[0].contin_bestFit.Y * 10, sy=[1, 0.3, 4], legend='relax. time distribution')

# determine the peak areas of the two peaks
ff = resx[0].contin_bestFit
p1 = (10 < ff.X) & (ff.X < 100)
fp1 = trapz(ff.Y[p1], ff.X[p1]) / trapz(ff.Y, ff.X)
p2 = (100 < ff.X) & (ff.X < 10000)
fp2 = trapz(ff.Y[p2], ff.X[p2])
p[0].text('fraction %.2g' % fp1, 90, 1.5, color=4)
p[0].text('fraction %.2g' % fp2, 10000, 0.5, color=4)


# do the contin with the .X .Y data as intensity weighted relaxation time
resd = js.dls.contin(dls, a=173, tmin=1, tmax=1e5, typ=0, bgr=0.05, distribution='d', T=(273 + dls.Temperature))

p[0].plot(resd[0].contin_result_fit, li=5, sy=0, legend='contin result fit d')
p[1].plot(resd[0].contin_bestFit.X, resd[0].contin_bestFit.Y * 1, legend='contin radius d')

# wavevector
# q=4*np.pi*1,333/632e-9*sin(theta/2)
# D=1/(G*q*q)
# Rh=k*T/(6*np.pi*visc*D)
# Rh=k*T*q*q/(6*np.pi*visc)  * G  = ff *G
kb = 1.3806505e-23  # J/K
theta = np.deg2rad(dls.ScatteringAngle)
q = 4 * np.pi * 1.333 / 632e-9 * np.sin(theta / 2)  # in 1/m
ff = kb * (dls.Temperature + 273.15) * q * q / (0.06 * np.pi * dls.Viscosity / 1000.)  # m/s
# Rh=ff*G
# .X time is in microseconds -> 1e-6 s
p[1].plot(resx[0].contin_bestFit.X * 1e-6 * ff * 1e9, resx[0].contin_bestFit.Y * weight, sy=[2, 0.3, 8],
          legend='relax. time to Rh')

p[0].legend(x=30000, y=2)
p[1].legend(x=0.01, y=15)

positions = []
print(resd.contin_bestFit[0].ipeaks_name)
for res in resd:
    isort = np.argsort(res.contin_bestFit.ipeaks[:, 1])
    sortedpeaks = res.contin_bestFit.ipeaks[isort]
    meanposition = np.r_[res.MeasurementTimeSeconds, sortedpeaks[:, 1]]
    positions.append(meanposition)

print('peak positions', positions)
p.save('Examplecontinanalysis.png')

