import jscatter as js
import numpy as np

# Here we examine the effect of instrumental smearing for SAX (Kratky Camera, line! ) and SANS
# and how we can use the Lake algorithm for desmearing.

# some data
q = np.r_[0.01:7:0.01]
# obj = js.ff.sphere(q,5)
data = js.ff.ellipsoid(q, 2, 3)
# add background
data.Y += 2
# load data for beam width profile
empty = js.dA(js.examples.datapath + '/buffer_averaged_corrected_despiked.pdh', usecols=[0, 1],
              lines2parameter=[2, 3, 4])
# read beam length profile measurement for a slit (Kratky Camera)
beam = js.dA(js.examples.datapath + '/BeamProfile.pdh', usecols=[0, 1], lines2parameter=[2, 3, 4])

# fit beam width for line collimation with semitransparent beam stop
bwidth = js.sas.getBeamWidth(empty, 'auto')

# prepare measured beamprofile from beam measurement
mbeam = js.sas.prepareBeamProfile(beam, a=2, b=1, bxw=bwidth, dIW=1.)
# prepare profile with trapezoidal shape using explicit given parameters (using parameters from above to have equal)
tbeam = js.sas.prepareBeamProfile('trapez', a=mbeam.a, b=mbeam.b, bxw=bwidth, dIW=1)
# prepare profile SANS a la Pedersen in point collimation. This can be used for SAXS with smaller apertures too!
Sbeam = js.sas.prepareBeamProfile('SANS', detDist=2000, wavelength=0.4, wavespread=0.15)

if 0:
    p = js.sas.plotBeamProfile(mbeam)
    p = js.sas.plotBeamProfile(mbeam, p)

# smear
datasm = js.sas.smear(unsmeared=data, beamProfile=mbeam)
datast = js.sas.smear(unsmeared=data, beamProfile=tbeam)
datasS = js.sas.smear(unsmeared=data, beamProfile=Sbeam)
# add noise
datasm.Y += np.random.normal(0, 0.5, len(datasm.X))
datast.Y += np.random.normal(0, 0.5, len(datast.X))
datasS.Y += np.random.normal(0, 0.5, len(datasS.X))

# desmear again
ws = 11
NI = -15
dsm = js.sas.desmear(datasm, mbeam, NIterations=NI, windowsize=ws)
dst = js.sas.desmear(datast, tbeam, NIterations=NI, windowsize=ws)
dsS = js.sas.desmear(datasS, Sbeam, NIterations=NI, windowsize=ws)

# compare
p = js.grace(2, 1.4)
p.plot(data, sy=[1, 0.3, 3], le='original ellipsoid')
p.plot(dst, sy=0, li=[1, 2, 1], le='desmeared SAX line collimation')
p.plot(dsS, sy=0, li=[1, 2, 2], le='desmeared SANS')
p.plot(datasm, li=[3, 2, 1], sy=0, le='smeared SAX line collimation')
p.plot(datasS, li=[3, 2, 4], sy=0, le='smeared SANS')
p.yaxis(max=1e4, min=0.1, scale='l', label='Intensity / a.u.', size=1.7)
p.xaxis(label=r'q / nm\S-1', size=1.7)
p.legend(x=3, y=5500, charsize=1.7)
p.title('Smeared ellipsoid and desmearing by Lake algorithm')

# The conclusion is to better fit smeared models than to desmear and fit unsmeared models.
p.save('SASdesmearing.png')
