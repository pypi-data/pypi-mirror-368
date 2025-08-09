# A model for protein incoherent scattering
# neglecting coherent and maybe some other contributions

import jscatter as js
import numpy as np
import urllib
from jscatter.dynamic import convolve as conv
from jscatter.dynamic import transRotDiffusion
from jscatter.dynamic import diffusionHarmonicPotential

# get pdb structure file with 3rn3 atom coordinates and filter for CA positions in A
# this results in C-alpha representation of protein Ribonuclease A.
url = 'https://files.rcsb.org/download/3RN3.pdb'
pdbtxt = urllib.request.urlopen(url).read().decode('utf8')
CA = [line[31:55].split() for line in pdbtxt.split('\n') if line[13:16].rstrip() == 'CA' and line[:4] == 'ATOM']
# conversion to nm and center of mass
ca = np.array(CA, float) / 10.
cloud = ca - ca.mean(axis=0)
Dtrans = 0.086  # nm**2/ns  for 3rn3 in D2O at 20°C
Drot = 0.0163  # 1/ns
natoms = cloud.shape[0]

# A list of wavevectors and frequencies and a resolution.
# If bgr is zero we have to add it later after the convolution with resolution as constant instrument background.
# As resolution a single q independent (unrealistic) Gaussian is used.
ql = np.r_[0.1, 0.5, 1, 2:15.:2]
w = np.r_[-100:100:0.1]

# all together in a combined model  ----------------------------
start = {'s0': 0.5, 'm0': 0, 'a0': 1, 'bgr': 0.00}
resolution = lambda w: js.dynamic.resolution_w(w=w, **start)


def transrotsurf(t, q, Dt, Dr, exR, tau, rmsd):
    """
    In time domain for pure incoherent scattering

    t : times
    q :  wavevector
    Dt : translational diffusion
    Dr : rotational diffusion
    exR : outside this radius additional restricted diffusion with t0 u0
    tau : correlation time
    rmsd : root mean square displacement Ds=u0**2/t0

    """
    natoms = cloud.shape[0]
    # fraction of natoms close to surface
    fsurf = ((cloud ** 2).sum(axis=1) ** 0.5 > exR).sum()/natoms

    transrot = transRotDiffusion(t, q, cloud, Dr, Dt)  # all natoms
    loc = diffusionHarmonicPotential(t, q, tau, rmsd)  # of a single atom

    # combine both in loc
    # all atoms contribute to transrot but only fsurf to loc
    # here one might mix with coherent scattering
    loc.Y = transrot._Iqtinc/transrot.Iq_inc * ((1 - fsurf) + fsurf * loc.Y)

    loc.setattr(transrot, 'TR_')  # copy attributes prepend 'TR'
    loc.fsurf = fsurf

    return loc


def trs_fitmodel(wt, q, Dt, Dr, exR, tau, rmsd):
    """
    Assume NSE data (WASP@ILL) and backscattering data.

    wt : times from NSE or frequencies from BS
    other i put as above

    """
    if np.any(wt<0): # timedomain has no negative times
        # time2frequencyFF determines needed times to avoid spectral leakage
        res = js.dynamic.time2frequencyFF(timemodel=transrotsurf,
                                    resolution=resolution,
                                    w=wt,
                                    q=q, Dt=Dt, Dr=Dr, exR=exR, tau=tau, rmsd=rmsd)
    else:
        res = transrotsurf(wt, q, Dt, Dr, exR, tau, rmsd)

    return res