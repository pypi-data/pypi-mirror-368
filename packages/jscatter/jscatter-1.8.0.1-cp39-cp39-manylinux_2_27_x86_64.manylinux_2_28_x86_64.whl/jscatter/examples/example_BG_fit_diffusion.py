# -*- coding: utf-8 -*-

import jscatter as js
import numpy as np

# load example data and show them in a nice plot as
i5 = js.dL(js.examples.datapath + '/iqt_1hho.dat')

# make a fixed size plot with the data
p = js.grace(1.5, 1)
p.plot(i5, symbol=[-1, 0.4, -1], legend='Q=$q')
p.legend(charsize=1.)
p.yaxis(0.01, 1.1, scale='log', charsize=1.5, label='I(Q,t)/I(Q,0)')
p.title('Intermediate scattering function', size=2)
p.xaxis(charsize=1.5, label='t / ns')

# defining model to use in fit
# simple diffusion
diffusion = lambda A, D, t, wavevector, elastic=0: A * np.exp(-wavevector ** 2 * D * t) + elastic
# or if you want to include in a library with description
# see examples in formel and formfactor

# in the data we have X as coordinate for time so we have to map the name
# same for the wavevector which is usually 'q' in these data
# the wavevector is available in the data for all i as i5[i].q
# or as a list as i5.q
# so test these

# analyzing the data
# to see the results we open an errorplot with Y-log scale
i5.makeErrPlot(yscale='l')
# '----------------------------------------'
# ' a first try model which is bad because of fixed high elastic fraction'
i5.fit(model=diffusion,
       freepar={'D': 0.1, 'A': 1},
       fixpar={'elastic': 0.5},
       mapNames={'t': 'X', 'wavevector': 'q'})
# '--------------------------------------'
# ' Now we try it with constant D and a worse A as starting parameters'
i5.fit(model=diffusion,
       freepar={'D': 0.1, 'A': 18},
       fixpar={'elastic': 0.0},
       mapNames={'t': 'X', 'wavevector': 'q'})
print(i5.lastfit.D, i5.lastfit.D_err)
print(i5.lastfit.A, i5.lastfit.A_err)
# A is close to 1 (as it should be here) but the fits don't look good
# '--------------------------------------'
# ' A free amplitude dependent on wavevector might improve '
i5.fit(model=diffusion,
       freepar={'D': 0.1, 'A': [1]},
       fixpar={'elastic': 0.0},
       mapNames={'t': 'X', 'wavevector': 'q'})
# and a second plot to see the results of A
pr = js.grace()
pr.plot(i5.lastfit.wavevector, i5.lastfit.A, i5.lastfit.A_err, legend='A')
# The fit is ok only the chi^2 is to high in this case of simulated data
# '--------------------------------------'
# ' now with free diffusion coefficient dependent on wavevector; is this the best solution?'
i5.fit(model=diffusion,
       freepar={'D': [0.1], 'A': [1]},
       fixpar={'elastic': 0.0},
       mapNames={'t': 'X', 'wavevector': 'q'})

pr.clear()  # removes the old stuff
pr.plot(i5.lastfit.wavevector, i5.lastfit.D, i5.lastfit.D_err, legend='D')
pr.plot(i5.lastfit.wavevector, i5.lastfit.A, i5.lastfit.A_err, legend='A')
# Ahh
# Now the amplitude is nearly constant and the diffusion is changing
# the fit is ok
# '--------------------------------------'
# ' now with changing diffusion and constant amplitude '
i5.fit(model=diffusion,
       freepar={'D': [0.1], 'A': 1},
       fixpar={'elastic': 0.0},
       mapNames={'t': 'X', 'wavevector': 'q'})
pr.clear()  # removes the old stuff
pr.plot(i5.lastfit.wavevector, i5.lastfit.D, i5.lastfit.D_err, legend='D')

# Booth fits are very good, but the last has less parameter.
# From simulation i know it should be equal to 1 for all amplitudes :-))))).
