"""
A minimal example how to fit Iqt from NSE measurements on polyelectrolytes using finiteZimm
to demonstarte how to include H(Q) and S(Q) for Dcm.

For details on the physics see

Interchain Hydrodynamic Interaction and Internal Friction of Polyelectrolytes
Buvalaia, et al ACS Macro Letters 12(9):1218    DOI: 10.1021/acsmacrolett.3c00409

"""
import jscatter as js
import numpy as np

# the structure factor type and parameters should be determined by fitting of SAXS/SANS data
# only for simplicity we use the PercusYevick, molarity is determined by experimental conditions of NSE
# here the experimental R of the PercusYevick is determined from experimental data

q0 = np.r_[0.01:2:100j]


def collectivefiniteZIMM(t, q, Dt=None, mu=0.5, Rh=4, R=4,tint=0, mol=0.0003):
    # Hq can be determined integrating over Sq and using Rh as a fit parameter
    # We assume here a polymer with different hydrodynamic interaction compared to a sphere
    # internally SF is calculated and saved in _sf
    SF = js.sf.PercusYevick
    HqSq = js.sf.hydrodynamicFunct(q0, Rh=Rh, molarity=mol,
                                 structureFactor=SF,
                                 structureFactorArgs={'R': R}, )
    HqSq.Y =  HqSq.Y / HqSq._sf  # this makes the needed H(Q)/S(Q)
    hqsq = HqSq[:2]  # only first columns

    # Dt is determined inside finiteZimm , but can be changed
    Iqt = js.dynamic.finiteZimm(t, q, NN=212, pmax=25, l=0.24, Dcm=Dt, tintern=tint, Temp=273 + 60, mu=mu,
                                viscosity=1, Dcmfkt = hqsq)
    Iqt.setColumnIndex(iey=None)
    return Iqt


# simulate data, typical NSE times IN15@ILL
tlist = js.loglist(0.1,300,30)

p = js.grace(2,1)
p.multi(1,2)
p[0].xaxis(label='t / ns',scale='log')
p[1].xaxis(label='t / ns',scale='log')
p[0].yaxis(label='I(Q,t)/I(Q,0)')

# lowest Q corresponds to DLS as synthetic dataset added to Iqt from NSE
sim = js.dL()
for q in np.r_[0.026,0.25,0.4,0.8,1.2,1.4,1.8]:  # in 1/nm
    sim.append(collectivefiniteZIMM(t=tlist, q=q, mol=0.0003, R=8, Rh=4, mu=0.6))
p[0].plot(sim,sy=0,li=[1,3,1])
p[1].plot(sim,sy=0,li=[1,3,1])

sim2 = js.dL()
for q in np.r_[0.026,0.25,0.4,0.6,0.8,1.2,1.4]:  # in 1/nm
    sim2.append(collectivefiniteZIMM(t=tlist, q=q, mol=0.0003, R=7, Rh=4, mu=0.6))
p[0].plot(sim2,sy=0,li=[3,3,2])

sim3 = js.dL()
for q in np.r_[0.026,0.25,0.4,0.6,0.8,1.2,1.4]:  # in 1/nm
    sim3.append(collectivefiniteZIMM(t=tlist, q=q, mol=0.0003, R=8, Rh=6, mu=0.6))
p[1].plot(sim3,sy=0,li=[3,3,4])

p[0].text('DLS',x=300,y=0.8)
p[1].text('DLS',x=300,y=0.8)
p[0].title('Interaction influences low Q, specifically DLS')
p[1].title('Rh influences all Q as self diffusion changes')

# p.save('collectiveZimm.png', size=(2, 1), dpi=150)

if 0:
    # A fit to exp. NSE data might be done like this (using sim as measured data, no errors)
    # fixpar are determined from other experiments
    sim.fit(model=collectivefiniteZIMM,
                freepar={'Rh':4,'mu':0.6,'tint':1},
                fixpar={'R':6, 'mol':0.0003 },  # from exp. conditions
                mapNames={'t':'X'})


