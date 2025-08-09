import jscatter as js
import numpy as np
import scipy.constants as constants

adh = js.bio.fetch_pdb('4w6z.pdb1')
# the 2 dimers in are in model 1 and 2 and need to be merged into one.
adhmerged = js.bio.mergePDBModel(adh)

p = js.grace(1.4, 1)
p.multi(1, 2)

for cc, pdb in enumerate(['3rn3', '3pgk', adhmerged], 1):
    # create universe; M and Z are for wrong named Mg and Zn  in the pdb files
    uni = js.bio.scatteringUniverse(pdb, vdwradii={'M': 1.73, 'Z': 1.7})
    uni.setSolvent('1d2o1')

    # SANS scattering intensity with conversion to 10g/l mass concentration and 1/cm units
    uni.qlist = np.r_[0.01, 0.1:3:0.03, 3:10:0.1]
    protein = uni.select_atoms('protein')
    Iq = js.bio.nscatIntUniv(protein)
    # molarity for 1g/l concentration
    mol = 1/protein.masses.sum()  # molarity 1g/l
    c = 10 * constants.N_A*mol/1000*1e-14  # conversion from 1/nm² per particle to 1/cm for 10g/l concentration
    # coherent contribution
    p[0].plot(Iq.X, Iq.Y * c, sy=0, li=[1, 3, cc], le=pdb)
    # incoherent contribution
    p[0].plot(Iq.X, Iq._P_inc * c, sy=0, li=[3, 2, cc], le='')

    # effective diffusion as seen by NSE in the initial slope of a rigid protein
    D_hr = js.bio.hullRad(uni)
    Dt = D_hr['Dt'] * 1e2  # conversion to nm²/ps
    Dr = D_hr['Dr'] * 1e-12  # conversion to 1/ps
    uni.qlist = np.r_[0.01, 0.1:6:0.06]
    Dq = js.bio.diffusionTRUnivTensor(uni.residues, DTT=Dt, DRR=Dr)
    p[1].plot(Dq.X, Dq.Y/Dq.DTTtrace, sy=[-1, 0.6, cc, cc], le=pdb)
    p[1].plot(Dq.X, Dq._Dinc_eff/Dq.DTTtrace, sy=0, li=[1, 3, cc], le=pdb)

p[0].plot([0, 10], [0.06]*2, sy=0, li=[2, 3, 1], le='')
p[0].xaxis(label=r'Q / nm\S-1', scale='log', min=0.1, max=10)
p[0].yaxis(label=r'I(Q) / 1/cm', scale='log', min=1e-4, max=3)
p[1].xaxis(label=r'Q / nm\S-1', scale='log', min=0.1, max=6)
p[1].yaxis(label=['D(Q)/D(0)', 1.5, 'opposite'], min=0.98, max=1.4)
p[0].legend(x=1, y=2)
p[0].title('neutron scattering intensity')
p[1].title('scaled effective diffusion')
p[1].subtitle('transl. diffusion at q=0, increase due to rot. diffusion')
p[1].text(r'D\sincoh', x=0.1, y=1.28, charsize=1.5)
p[1].text(r'D\scoh', x=0.3, y=1.04, charsize=1.5)
p[0].text('incoherent', x=3.7, y=0.003, charsize=1.3)
p[0].text(r'D\s2\NO background', x=1.7, y=0.038, charsize=1.3)
# p.save('bio_protein_formfactor+Diffusion.png')

