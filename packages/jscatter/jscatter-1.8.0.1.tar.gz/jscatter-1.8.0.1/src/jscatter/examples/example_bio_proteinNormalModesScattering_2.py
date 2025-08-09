"""
Alcohol dehydrogenase (yeast) example for normal mode analysis
See Biehl et al.PRL 101, 138102 (2008)

Here we build from part 1 a model that can be used for fitting
"""

# A fit model to fit Iqt from NSE measurements
# Include H(Q) and S(Q)
# and repeat what we need from part 1

%matplotlib
import jscatter as js
import numpy as np

# create universe
adh = js.bio.fetch_pdb('4w6z.pdb1')
adhmerged = js.bio.mergePDBModel(adh)
u = js.bio.scatteringUniverse(adhmerged)
u.setSolvent('1d2o1')
u.qlist = js.loglist(0.1, 5, 100)
u.atoms.deuteration = 0
protein = u.select_atoms('protein')
S0 = js.bio.nscatIntUniv(protein, cubesize=0.5, getVolume='once')


# structure factor Sq and hydrodynamic function Hq
# This should be determined from SAXS/SANS measurements at same concentration like NSE
# and maybe fit including concentration dependence
mol = 0.0003
R=4
def Sqbeta(q, R, molarity):
    # this function should be used for structure factor fitting of experimental data
    # as it contains the shape correction from Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983)
    # structure factor without correction
    Sq = js.sf.PercusYevick(q=q, R=R, molarity=molarity)  # about 50mg/ml protein like experimental data
    # factor beta from formfactor calculation
    beta = S0.interp(q, col='beta')
    # correct Sq for beta
    Sq.Y = 1 + beta * (Sq.Y-1)
    return Sq

# Hq can be determined by fitting Rh or be determined by other measurements
# We assume here larger hydrodynamic interaction
# The Kotlarchyk correction from above is included by using Sqbeta
Hq = js.sf.hydrodynamicFunct(S0.X, Rh=R*1.1, molarity=mol,
                             structureFactor=Sqbeta,
                             structureFactorArgs={'R': R}, )


# look at the  D_t = D_0 H(Q)/S(Q) correction for translational diffusion
p3 = js.mplot()
p3.plot(Hq.X,Hq._sf,le='S(Q)')
p3.plot(Hq,le='H(Q)')
p3.plot(Hq.X, Hq.Y/Hq._sf,le='H(Q)/S(Q)')
p3.Yaxis(label='S(Q), H(Q), H(Q)/S(Q)')
p3.Xaxis(min=0.,max=4,label='$Q / nm^-1$')
p3.Title('structure factor and hydrodynamic function\n for translational diffusion')
p3.Text('$H(Q=\infty)/S(Q=\infty)$ can be estimated \nfrom viscosity measurements \nor PFG-NMR.',x=2,y=0.8)
p3.Text('$H(Q=0)/S(Q=0)$ can be measured by DLS.',x=0.8,y=0.95)
p3.Legend()
# p3.savefig(js.examples.imagepath+'/ADHNM_SqHq.jpg', dpi=100)

D_hr = js.bio.hullRad(u)
Dt = D_hr['Dt'] * 1e2  # conversion to nm²/ps
Dr = D_hr['Dr'] * 1e-12  # conversion to 1/ps
# u.qlist = np.r_[0.01, 0.1:3:0.2]
Deff = js.bio.diffusionTRUnivTensor(u.residues, DTT=Dt, DRR=Dr, cubesize=0.5)

# make normal modes and calc A(Q)
ca = u.residues
nm = js.bio.vibNM(ca)
Ph678 = js.dL()
for NN in [6,7,8]:
   Ph = js.bio.intScatFuncPMode(nm, NN, output=0, qlist=Deff.X)
   Ph678.append(Ph)
sumP = Ph678.Y.array.sum(axis=0)


def Aq(a):
    aq = a**2*sumP / (Ph678[0]._Fq + a**2*sumP)
    A = js.dA(np.c_[Ph678[0].X, aq].T)
    A.rmsdNM = a * Ph678.kTrmsdNM.array.sum()
    return A

# this is the model for a fit
def transRotModes(t, q, Dt, Dr, Rhf=1, R=4, a=1000, l=10, mol=0.0003):
    # trans rot diffusion including H(Q)/S(Q)
    # default values for R, mol are determined from preparation or experiments

    Sq = Sqbeta(q=q, R=R, molarity=mol)
    # assume a factor between the interaction radius R and hydrodynamic radius Rh
    Hq = js.sf.hydrodynamicFunct(q, Rh=R*Rhf, molarity=mol, structureFactor=Sqbeta,
                                structureFactorArgs={'R': R}, )

    Dth = Dt * Hq.interp(q) / Sq.interp(q)
    # assume Hr =1-(1-DsoverD0)/3 for rotational diffusion
    Drh = Dr*(1-(1-Hq.DsoverD0)/3)
    Iqt = js.bio.intScatFuncYlm(u.residues, qlist=np.r_[q],tlist=t, Dtrans=Dth, Drot=Drh, cubesize=1)[0]
    
    # add Pmode relaxation
    Aqa = Aq(a)
    diff = Iqt.Y *(1-Aqa.interp(q))
    Iqt.Y = Iqt.Y *((1-Aqa.interp(q)) + Aqa.interp(q)*np.exp(-1/(l*1000)*Iqt.X))
    Iqt2 = Iqt.addColumn(1,diff)
    
    # for later reference in lastfit save parameters
    Iqt2.Dt = Dt
    Iqt2.Dr = Dr
    Iqt2.H0= Hq.DsoverD0
    Iqt2.R = R
    Iqt2.Rh = R * Rhf
    Iqt2.rmsdNM = Aqa.rmsdNM

    return Iqt2

# simulate data
tlist = np.r_[1, 10:1e5:50]
sim = js.dL()
for q in np.r_[0.25,0.5,0.9,1.2,2]:
    sim.append(transRotModes(t=tlist, q=q, Dt=Dt, Dr=Dr,a=100,l=10))

p4=js.mplot()
for c, si in enumerate(sim,1):
    p4.plot(si,sy=0,li=[1,2,c],le=f'$Q={si.q} nm^{-1}$')
    p4.plot(si.X,si[2], sy=0, li=[3,2,c ])
p4.Yaxis(min=0.01,max=1,label='I(Q,t)/I(Q,0)',scale='log')
p4.Xaxis(min=0.1,max=100000,label='t / ps')
p4.Title('Intermediate scattering function')
p4.Subtitle(f'rmsd = {si.rmsdNM:.2f} nm')
p4.Legend()
# p4.savefig(js.examples.imagepath+'/ADHNM_IQTsim.jpg', dpi=100)

if 0:
    # A fit to exp. NSE data might be done like this (using sim as measured data)
    # fixpar are determined from other experiments (e.g. Dt0 extrapolating DLS to zero conc.)
    # or Dr0 from calculation from structure (using HULLRAD or HYDROPRO), mol from sample preparation
    Dt0 = 4.83e-05   #  nm²/ps
    Dr0 = 1.64e-06  #  1/ps
    sim.fit(model=transRotModes,
                freepar={'Rhf':1, 'a':100, 'l':10},
                fixpar={'Dt':Dt0, 'Dr':Dr0,'R':4, 'mol':0.0003 },
                mapNames={'t':'X'})


