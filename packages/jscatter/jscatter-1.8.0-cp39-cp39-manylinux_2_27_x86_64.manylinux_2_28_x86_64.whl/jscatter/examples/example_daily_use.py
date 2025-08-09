# in nutshell without fine tuning of plots

import jscatter as js
import numpy as np

# read data with 16 intermediate scattering functions from NSE measurement of protein diffusion
i5 = js.dL(js.examples.datapath + '/iqt_1hho.dat')

# manipulate data
for dat in i5:
    dat.X = dat.X /1.  # conversion from ps to ns
    dat.q *= 1  # conversion to 1/nm if needed

# define model as simple diffusion with elastic background
diffusion = lambda A, D, t, elastic, wavevector=0: A * np.exp(-wavevector ** 2 * D * t) + elastic

# make ErrPlot to see progress of intermediate steps with residuals (updated all 2s)
i5.makeErrPlot(title='diffusion model residual plot', legpos=[0.2, 0.8])

# fit it
i5.fit(model=diffusion,  # the fit function
       freepar={'D': [0.2, 0.25], 'A': 1},  # fit start values; [..] indicate independent fit parameter
       fixpar={'elastic': 0.0},             # single values indicates common fit parameter
       mapNames={'t': 'X', 'wavevector': 'q'},  # map names of the model to names of data attributes
       condition=lambda a: (a.X > 0.01) & (a.Y > 0.01))  # a condition to include only specific values

# save fit result with errors and covariance matrix
i5.lastfit.savetxt('iqt_proteindiffusion_fit.dat')

# plot it together with lastfit result
p = js.grace()
p.plot(i5, symbol=[-1, 0.4, -1], legend='Q=$q')  # plot as alternating symbols and colors with size 0.4
p.plot(i5.lastfit, symbol=0, line=[1, 1, -1])  # plot a line with alternating colors
p.save('iqt_proteindiffusion_fit.png')

# plot result with error bars
p1 = js.grace(2, 2)  # plot with a defined size
p1.plot(i5.lastfit.wavevector, i5.lastfit.D, i5.lastfit.D_err, symbol=[2, 1, 1, ''], legend='average effective D')
p1.save('Diffusioncoefficients.agr')  # save as XmGrace plot
