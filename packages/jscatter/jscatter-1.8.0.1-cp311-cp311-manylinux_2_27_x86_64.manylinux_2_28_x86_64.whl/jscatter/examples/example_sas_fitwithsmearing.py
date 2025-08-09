import jscatter as js
import numpy as np

# prepare beamprofiles according to measurement setup
# SAXS with small resolution
fbeam = js.sas.prepareBeamProfile(0.01)
# low and high Q SANS
Sbeam4m = js.sas.prepareBeamProfile('SANS', detDist=4000, wavelength=0.4, wavespread=0.1)
Sbeam20m = js.sas.prepareBeamProfile('SANS', detDist=20000, wavelength=0.4, wavespread=0.1)


# define smeared model with beamProfile as parameter
@js.sas.smear(beamProfile=fbeam)
def smearedsphere(q, R, bgr, contrast=1, beamProfile=None):
    sp = js.ff.sphere(q=q, radius=R, contrast=contrast)
    sp.Y = sp.Y + bgr
    return sp


# read data with 3 measurements
smeared = js.dL(js.examples.datapath+'/smearedSASdata.dat')

# add corresponding smearing to the datasets
# that the model can see in attribute beamprofile how to smear
smeared[0].beamProfile = fbeam
smeared[1].beamProfile = Sbeam4m
smeared[2].beamProfile = Sbeam20m

if 0:
    # For scattering data it is sometimes advantageous
    # to use a log weight in fit using the error weight
    for temp in smeared:
        temp.eY = temp.eY *np.log(temp.Y)

# fit it
smeared.setlimit(bgr=[0.01])
smeared.makeErrPlot(yscale='l', fitlinecolor=[1, 2, 5], title='Multi smeared model fit')
smeared.fit(smearedsphere, {'R': 12, 'bgr': 0.1, 'contrast': 1e-2}, {}, {'q': 'X'})
# smeared.errplot.save(js.examples.imagepath+'/smearedfitexample.png')


sys.exit()  # end
# creating smeared synthetic data for above
# smear data and add individual beam profiles


# the unsmeared model
def sphere(q, R, bgr, contrast=1):
    sp = js.ff.sphere(q, R, contrast)
    sp.Y = sp.Y + bgr
    return sp

fbeam = js.sas.prepareBeamProfile(0.01)
Sbeam4m = js.sas.prepareBeamProfile('SANS', detDist=4000, wavelength=0.4, wavespread=0.1, extrapolfunc=['guinier',None])
Sbeam20m = js.sas.prepareBeamProfile('SANS', detDist=20000, wavelength=0.4, wavespread=0.1, extrapolfunc=['guinier',None])

q = js.loglist(0.01, 2, 300)
data = sphere(q, R=13, bgr=0.1, contrast=1e-2)
data.setColumnIndex(iey=2)
data.Y = np.abs(data.Y + np.random.randn(data.shape[1]) * 0.01)
data.eY = np.abs(data.Y) * np.log(data.Y) * 0.003 +0.01


smeared = js.dL()
smeared.append(js.sas.smear(unsmeared=data, beamProfile=fbeam).prune(lower=0.05)[:3])
smeared[-1].setColumnIndex(iey=2)
smeared[-1].eY = data.prune(lower=0.05).eY
del smeared[-1].beamProfile
smeared.append(js.sas.smear(unsmeared=data, beamProfile=Sbeam4m).prune(lower=0.3)[:3])
smeared[-1].setColumnIndex(iey=2)
smeared[-1].eY = data.prune(lower=0.3).eY
del smeared[-1].tckUnsm
del smeared[-1].beamProfile
smeared.append(js.sas.smear(unsmeared=data, beamProfile=Sbeam20m).prune(upper=0.7)[:3])
smeared[-1].setColumnIndex(iey=2)
smeared[-1].eY = data.prune(upper=0.7).eY
del smeared[-1].tckUnsm
del smeared[-1].beamProfile
smeared.save(js.examples.datapath+'/smearedSASdata.dat')

