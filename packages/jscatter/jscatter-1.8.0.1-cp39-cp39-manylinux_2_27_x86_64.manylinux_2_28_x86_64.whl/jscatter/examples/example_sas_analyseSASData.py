# Analyse SAS data by extrapolating the form factor followed by structure factor determination

import jscatter as js
import numpy as np

# generate some synthetic data just for this demonstration
# import the model described in example_buildComplexModel
# it describes ellipsoids with PercusYevick structure factor
from jscatter.examples import particlesWithInteraction as PWI

NN = 100
q = js.loglist(0.1, 5, NN)
data = js.dL()
bgr = js.dA(np.c_[q, 0.2 + np.random.randn(NN) * 1e-3, [1e-3] * NN].T)  # background
for m in [0.02, 0.05, 0.2, 0.6]:
    pwi = PWI(q, Ra=3, Rb=4, molarity=m * 1e-3, bgr=0, contrast=6e-4)
    pwi = pwi.addColumn(1, np.random.randn(NN) * 1e-3)
    pwi.Y = pwi.Y + bgr.Y
    pwi.setColumnIndex(iey=-1)
    data.append(pwi)

# With measured data the above is just reading data and background
# with an attribute molarity or concentration.
# This might look like this
if 0:
    data = js.dL()
    bgr = js.dA('backgroundmeasurement.dat')
    for name in ['data_conc01.dat', 'data_conc02.dat', 'data_conc05.dat', 'data_conc08.dat']:
        data.append(name)
        data[-1].molarity = float(name.split('.')[0][-2:])

p = js.grace(2, 0.8)
p.multi(1, 4)
p[0].plot(data, sy=[-1, 0.3, -1], le='c= $molarity M')
p[0].yaxis(min=1e-4, max=1e2, scale='l', label=r'I(Q) / cm\S-1', tick=[10, 9], charsize=1, ticklabel=['power', 0, 1])
p[0].xaxis(scale='l', label=r'Q / nm\S-1', min=1e-1, max=1e1, charsize=1)
p[0].text(r'original data\nlike from measurement', y=50, x=1)
p[0].legend(x=0.12, y=0.003)

# Using the synthetic data we extract again the form factor and structure factor
# subtract background and scale data by concentration or volume fraction
datas = data.copy()
for dat in datas:
    dat.Y = (dat.Y - bgr.Y) / dat.molarity
    dat.eY = (dat.eY + bgr.eY) / dat.molarity  # errors increase
p[1].plot(datas, sy=[-1, 0.3, -1], le='c= $molarity M')
p[1].yaxis(min=1, max=1e5, scale='l', tick=[10, 9], charsize=1, ticklabel=['power', 0])
p[1].xaxis(scale='l', label=r'Q / nm\S-1', min=1e-1, max=1e1, charsize=1)
p[1].text(r'bgr subtracted and\n conc. scaled', y=5e4, x=0.8)

# extrapolate to zero concentration to get the  form factor
# dataff=datas.extrapolate(molarity=0,func=lambda y:-1/y,invfunc=lambda y:-1/y)
dataff = datas.extrapolate(molarity=0)[0]
# as error *estimate* we may use the mean of the errors which is not absolutely correct
dataff = dataff.addColumn(1, datas.eY.array.mean(axis=0))
dataff.setColumnIndex(iey=2)
p[2].plot(datas[0], li=[1, 2, 4], sy=0, le='low molarity')
p[2].plot(dataff, sy=[1, 0.5, 1, 1], le='extrapolated')
p[2].yaxis(min=1, max=1e5, scale='l', tick=[10, 9], charsize=1, ticklabel=['power', 0])
p[2].xaxis(scale='l', label=r'Q / nm\S-1', min=1e-1, max=1e1, charsize=1)
p[2].legend(x=0.13, y=200)
p[2].text(r'extrapolated formfactor \ncompared to lowest conc.', y=5e4, x=0.7)

# calc the structure factor by dividing by the form factor
sf = datas.copy()
for dat in sf:
    dat.Y = dat.Y / dataff.Y
    dat.eY = (dat.eY ** 2 / dataff.Y ** 2 + dataff.eY ** 2 * (dat.Y / dataff.Y ** 2) ** 2) ** 0.5
    dat.volfrac = dat.Volume * dat.molarity
p[3].plot(sf, sy=[-1, 0.3, -1], le=r'\xF\f{}= $volfrac')
p[3].yaxis(min=0, max=2, scale='n', label=['S(Q)', 1, 'opposite'], charsize=1, ticklabel=['General', 0, 1, 'opposite'])
p[3].xaxis(scale='n', label=r'Q / nm\S-1', min=1e-1, max=2, charsize=1)
p[3].text('structure factor', y=1.5, x=1)
p[3].legend(x=0.8, y=0.5)

# remember so safe the form factor and structurefactor
# sf.save('uniquenamestructurefactor.dat')
# dataff.save('uniquenameformfactor.dat')

# save the figures
p.save('SAS_sf_extraction.agr')
p.save('SAS_sf_extraction.png', size=(2500/300, 1000/300), dpi=300)
