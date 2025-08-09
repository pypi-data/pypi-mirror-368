# in nutshell without fine tuning of plots

import jscatter as js
import numpy as np

# generate the data
q=js.loglist(0.1,5,100)
da = js.dL()
da.append(js.ff.sphereGaussianCorona(q,R=4,Ncoil=10,Nmonomer=150,monomerVolume=0.12,a=0.8, coilSLD=-0.56e-4, sphereSLD=6.3e-4, solventSLD=-0.56e-4)[:2])
da.append(js.ff.sphereGaussianCorona(q,R=4,Ncoil=10,Nmonomer=150,monomerVolume=0.12,a=0.8, coilSLD=-0.56e-4, sphereSLD=6.3e-4, solventSLD=3e-4)[:2])
da.append(js.ff.sphereGaussianCorona(q,R=4,Ncoil=10,Nmonomer=150,monomerVolume=0.12,a=0.8, coilSLD=-0.56e-4, sphereSLD=6.3e-4, solventSLD=6.3e-4)[:2])
# add errors
e = 2e-5
da[0] = da[0].addColumn(1, e)
da[1] = da[1].addColumn(1, e)
da[2] = da[2].addColumn(1, e)
da.setColumnIndex(iey=2)
# and some randomness
da[0].Y = da[0].Y + np.random.rand(len(q)) * e
da[1].Y = da[1].Y + np.random.rand(len(q)) * e
da[2].Y = da[2].Y + np.random.rand(len(q)) * e
for dd in da:
    # add structure factor
    dd.Y *= js.sf.PercusYevick(q, 8, eta=0.1).Y
# da.save(js.examples.datapath + '/gauscoronna.dat')

p=js.grace()
p.plot(da)
p.yaxis(label='I(q)',scale='l',min=1e-6,max=0.1)
p.xaxis(label='q / nm\S-1',scale='l')
p.legend(x=0.15,y=0.0002)

# end generate data #########################

import jscatter as js

# read data measured at 3 contrast conditions:
i5 = js.dL(js.examples.datapath + '/gauscoronna.dat')
# add solvent contrast to data from preparation, will be used as fixed parameter per dataArray
i5[0].solventSLD = -0.56e-4    # H2O contrast (nearly its actually lower, but this is just an example)
i5[1].solventSLD = 3e-4        # some H2O/D2O mixture
i5[2].solventSLD = 6.3e-4      # D2O
i5.setlimit(bgr=[0, 0.00001], RPY=[0, 20])


# define sphereGaussianCorona with background
def coreCoilCoronna(q, R, Ncoil, Nmonomer, monomerVolume, a, coilSLD, sphereSLD, solventSLD, RPY,eta,bgr):
    res = js.ff.sphereGaussianCorona(q, R=R, Ncoil=Ncoil,Nmonomer=Nmonomer,monomerVolume=monomerVolume,a=a ,
                                     coilSLD=coilSLD, sphereSLD=sphereSLD, solventSLD=solventSLD)
    res.Y =res.Y * js.sf.PercusYevick(q, RPY, eta=eta).Y + bgr
    return res


# make ErrPlot to see progress of intermediate steps with residuals (updated all 2 seconds)
i5.makeErrPlot(title='simultaneous fit contrast matching', xscale='log', yscale='log', legpos=[0.12, 0.5])

# fit it
# the minimum in core contrast can be used to predetermine "R":4
# Method 'Nelder-Mead' searches more for a solution,direct use of 'lm' works here
i5.fit(model=coreCoilCoronna,  # the fit function
       freepar={ 'Ncoil': 8, 'Nmonomer':100,
                 'coilSLD': 3e-4, 'sphereSLD': 3e-4, 'bgr': 0, 'RPY':7,'eta':0.1},
       fixpar={'R': 4, 'a':0.8, 'monomerVolume':0.12},
       mapNames={'q': 'X', })

# use a 'lm' to polish the result and get errors using the last fit result as start
# here this really improves the fit
i5.estimateError()

# i5.errplot.save(js.examples.imagepath+'/multicontrastfit.png', size=(1.5, 1.5))

