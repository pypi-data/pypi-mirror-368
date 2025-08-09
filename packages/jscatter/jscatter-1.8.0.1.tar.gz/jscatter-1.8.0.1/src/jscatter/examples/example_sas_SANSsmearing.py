import jscatter as js
import numpy as np

# prepare profiles SANS for typical 2m and 8m measurement
# smear calls resFunc with the respective parameters; smear also works with line collimation SAXS if needed
resol8m = js.sas.prepareBeamProfile('SANS', collDist=8000., collAperture=10, detDist=8000., sampleAperture=10,
                                    wavelength=0.5, wavespread=0.2, dpixelWidth=10, dringwidth=1)


# demonstration smearing effects

# define model and use @smear to wrap it with the smearing function
# detDist and collDist will be used in js.sas.smear to change the beamprofile for smearing

@js.sas.smear(beamProfile=resol8m)
def ellipsoid(q, a, b, bgr, detDist=2000, collDist=2000.):
    elli = js.ff.ellipsoid(q, a, b)
    elli.Y = elli.Y + bgr
    return elli


# generate some smeared data, or load them from measurement
a, b = 2, 3
data = js.dL()
data.append(ellipsoid(np.r_[0.01:1:0.01], a, b, 2, detDist=8000, collDist=8000.))
data.append(ellipsoid(np.r_[0.5:5:0.05], a, b, 2, detDist=2000, collDist=2000.))

# here we compare the difference between the 2 profiles using for both the full q range
data2 = js.dL()
data2.append(ellipsoid(np.r_[0.01:5:0.02], a, b, 2, detDist=8000, collDist=8000.))
data2.append(ellipsoid(np.r_[0.01:5:0.02], a, b, 2, detDist=2000, collDist=2000.))

# plot it
p = js.grace()
ellip = js.ff.ellipsoid(np.r_[0.01:5:0.01], a, b)
ellip.Y += 2
p.plot(ellip, sy=[1, 0.3, 1], legend='unsmeared ellipsoid')
p.yaxis(label='Intensity / a.u.', scale='l', min=1, max=1e4)
p.xaxis(label=r'Q / nm\S-1', scale='n')
p.plot(data, legend='smeared $rf_detDist')
p.plot(data2[0], li=[1, 1, 4], sy=0, legend='8m smeared full range')
p.plot(data2[1], li=[3, 1, 4], sy=0, legend='2m smeared full range')
p.legend(x=2.5, y=8000)
p.title('SANS smearing of ellipsoid')
p.save('SANSsmearing.jpg')

# now we use the simulated data to fit this to a model
# the data need attributes detDist and collDist to use correct parameters in smearing
# here we add these from above in rf_detDist (set in smear)
# for a measurement this needs to be added to the experimental data
data[0].detDist = data[0].rf_detDist
data[0].collDist = data[0].rf_collDist
data[1].detDist = data[1].rf_detDist
data[1].collDist = data[1].rf_collDist


@js.sas.smear(beamProfile=resol8m)
def smearedellipsoid(q, A, a, b, bgr, detDist=2000, collDist=2000.):
    """
    The model may use all needed parameters for smearing.
    """
    ff = js.ff.ellipsoid(q, a, b)  # calc model
    ff.Y = ff.Y * A + bgr  # multiply amplitude factor and add bgr
    return ff


# fit it , here no errors
data.makeErrPlot(yscale='l', fitlinecolor=[1, 2, 5])
data.fit(smearedellipsoid, {'A': 1, 'a': 2.5, 'b': 3.5, 'bgr': 0}, {}, {'q': 'X'})
# show the unsmeared model
p = js.grace()
for oo in data:
    p.plot(oo, sy=[-1, 0.5, -1], le='lastfit smeared')
    p.plot(oo.X, oo[2], li=[3, 2, 4], sy=0, legend='lastfit unsmeared')
p.yaxis(scale='l')
p.legend()
p.save('SANSsmearingFit.jpg')
