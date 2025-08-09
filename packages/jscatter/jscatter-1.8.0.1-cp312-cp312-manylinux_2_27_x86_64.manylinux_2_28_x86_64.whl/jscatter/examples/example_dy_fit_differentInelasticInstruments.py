# A model for protein incoherent scattering
# neglecting coherent and maybe some other contributions

# We use real data but a strongly simplified model ignoring rotational diffusion of the protein,
# D2O contribution and  dihedral CH3 motions visible in IN5 data.
# Therefore the results are yet not to over interpret even if the diffusion coefficient is not bad.
# The intention is to give an example how to fit different instruments together

import jscatter as js
import numpy as np
from jscatter.dynamic import convolve
from jscatter.dynamic import diffusionHarmonicPotential_w, transDiff_w



def readinx(filename, block, l2p, instrument):
    # reusable function for inx reading
    # neutron scatterers use strange data formats like .inx dependent on local contact
    # the blocks start with  number of channels. Spaces (' 562 ') are important to find the starting line.
    # this might dependent on instrument
    data = js.dL(filename,
                 block=block,  # this finds the starting of the blocks of all angles or Q
                 usecols=[1, 2, 3],  # ignore the numbering at each line
                 lines2parameter=l2p)  # catch the parameters at beginning
    for da in data:
        da.channels = da.line_1[0]
        da.Q = da.line_3[0]  # in 1/A
        da.incident_energy = da.line_3[1]  # in meV
        da.temperature = da.line_3[3]  # in K if given
        da.instrument = instrument
    return data

# recover fit of resolution
# see js.dynamic.resolution_w in examples how this was fitted
vana_spheres = js.dL(js.examples.datapath + '/Vana_fitted.inx.gz')
vana_spheres.getfromcomment('modelname')

# read new data
adh = readinx(js.examples.datapath + '/ADH.inx.gz', block=' 563 ', l2p=[-1, -2, -3, -4, -5],instrument='spheres')

# convert to 1/ns
adhf = js.dynamic.convert_e2w(adh, 293, unit='μeV')


def trs_fitmodel(wt, dw, Q, DD, floc, tau, rmsd, A, bgr, instrument):
    """
    Assume NSE data (WASP@ILL) and backscattering (BS) data.
    BS need the convolution with resolution while NSE data are always resolution corrected.

    wt : times from NSE or frequencies from BS
    other input as above

    """
    if instrument in ['spheres','in5']:
        w = wt  # increase w to avoid boundary effects
        # get right Q value of resolution for selected instrument
        if instrument == 'spheres':
            resolutionQ = vana_spheres.filter(Q=Q)[0]
            resolution = js.dynamic.resolution_w(w=w, resolution=resolutionQ)
        elif instrument == 'IN5':
            resolutionQ = vana_IN5.filter(Q=Q)[0]
            resolution = js.dynamic.resolution_w(w=w, resolution=resolutionQ)

        # The model is the same for these instruments

        # localized diffusion in rmsd with tau
        loc = diffusionHarmonicPotential_w(w, Q, tau, rmsd)
        loc.Y = js.dynamic.elastic_w(w).Y * (1 - floc) + floc * loc.Y  # add elastic fraction
        locw = convolve(loc, resolution, normB=True)

        # translational diffusion
        trans = transDiff_w(w, Q, DD)
        transw = convolve(trans, resolution, normB=True)

        transloc = convolve(trans, loc)
        transloc.floc = floc

        res = convolve(transloc, resolution, normB=True)
        # add amplitude and background
        res.Y = A * res.Y + bgr
        res.X = res.X + resolutionQ.w0 + dw

        # append some of the intermediate contributions
        res = res.addColumn(1,A*transw.Y*(1-floc)+bgr)
        res = res.addColumn(1, A * locw.Y * floc + bgr)
        res = res.addColumn(1,resolution.interp(wt)+bgr)
        res.columnname='w;tl;t;l;r'  # name the columns for easier access

    elif instrument == 'JNSE':
        # a NSE machine operating in time domain needs a different model (not yet)
        t = wt
        res = transrotsurf(t, Q, DD, floc, tau, rmsd)

    # interpolate to needed scale points
    return res.interpAll(wt)

# use reduce data for first faster fitting; use all later
adh2 = adhf[1::3]

# fit single dataArray
ad = adh2[-1]
ad.makeErrPlot(yscale='log', title=str(ad.Q) + ' A\S-1')
ad.setlimit(A=[0, 10000], bgr=[0, 10], DD=[0.005, 10], floc=[0.1, 0.9, 0, 1], tau=[0, 2], rmsd=[0, 20],dw=[-2,2])
ad.fit(trs_fitmodel,
       {'A': 90, 'DD': 0.5,'bgr': 1,  'floc': 0.8, 'tau': 0.1, 'rmsd': 1,'dw':0},
       {},
       {'wt': 'X'},
       method='Nelder-Mead',max_nfev=20000)

ad.errplot.plot(ad.lastfit.X,ad.lastfit._t,li=[1,3,2],sy=0,le='trans')
ad.errplot.plot(ad.lastfit.X,ad.lastfit._l,li=[1,3,4],sy=0,le='loc')
ad.errplot.legend()


# fit all together with common DD, floc, rmsd, tau and independent A and bgr
ad5 = adhf[1::3]
ad5.makeErrPlot(yscale='log', title=fr'{str(ad5.Q)} A\S-1',residual='rel')
ad5.setlimit(A=[0, 10000], bgr=[0, 10], DD=[0.005, 10], floc=[0.01, 0.9, 0, 1], tau=[0, 20], rmsd=[0, 20],dw=[-2,2])
ad5.fit(trs_fitmodel,
        {'A': [90], 'DD': 0.05,'bgr': [1],  'floc': 0.8, 'tau': 0.1, 'rmsd': 1,},
        {'dw':[0]},
        {'wt': 'X'},
        max_nfev=20000)

ad5.savelastErrPlot('inelasticInstruments_together.png', size=(2, 1.5), dpi=400)

# check diffusion
ad5.DD
ad5.DD_err

# inspect one of the overall fit
p = js.grace()
p.yaxis(scale='log')
p.title(f'Q={ad5[-1].Q} A\S-1')
p.plot(ad5[-1])
p.plot(ad5.lastfit[-1],sy=0,li=[1,2,14],le='fit')
p.plot(ad5.lastfit[-1].X,ad5.lastfit[-1]._l,sy=0,li=[1,2,10],le='local')
p.plot(ad5.lastfit[-1].X,ad5.lastfit[-1]._t,sy=0,li=[1,2,4],le='diffusion')
p.legend()
p.save('inelasticInstruments_one.png', size=(2, 1.5), dpi=400)

