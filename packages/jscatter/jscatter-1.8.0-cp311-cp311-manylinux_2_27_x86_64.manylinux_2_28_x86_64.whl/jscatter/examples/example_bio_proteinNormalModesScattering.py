""" Alcohol dehydrogenase (yeast) example for normal mode analysis
#
# See Biehl et al.PRL 101, 138102 (2008)

In this example we consecutivly
 - load the protein
 - create normal modes
 - calc effective diffusion
 - calc the dynamic mode formfactor from normal modes
 - show how the intermediate scattering function looks with diffusion and internal normal mode relaxation

Finally, we build from this a model that can be used for fitting

"""

# create universe with protein inside that adds hydrogen
#  - load PDB structure
#  - repair structure e.g. missing atoms 
#  - add hydrogen using pdb2pqr, saving this to 3cln_h.pdb
#  - adds scattering amplitudes, volume determination

%matplotlib
import jscatter as js
import numpy as np

adh = js.bio.fetch_pdb('4w6z.pdb1')
# the 2 dimers in are in model 1 and 2 and need to be merged into one.
adhmerged = js.bio.mergePDBModel(adh)
u = js.bio.scatteringUniverse(adhmerged)
u.atoms.deuteration = 0
protein = u.select_atoms("protein")
S0 = js.bio.nscatIntUniv(protein, cubesize=0.5, getVolume='once')

# ## Calc effective diffusion with trans/rot contributions
# - determine $D_{trans}$ and $D_{rot}$ using HULLRAD
# - calc Deff
D_hr = js.bio.hullRad(u)
Dt = D_hr['Dt'] * 1e2  # conversion to nm²/ps
Dr = D_hr['Dr'] * 1e-12  # conversion to 1/ps
u.qlist = np.r_[0.01, 0.1:3:0.2]
Deff = js.bio.diffusionTRUnivTensor(u.residues, DTT=Dt, DRR=Dr, cubesize=0.5)

p=js.mplot()
p.Plot(Deff.X, Deff.Y*1e5, li=1, le='rigid ADH protein')
p.Xaxis(label='$Q / nm^{-1}$')
p.Yaxis(label='$D_{eff} /A^2/ns$')

# ## Create normal modes based on residues
nm = js.bio.vibNM(protein.residues,k_b=418)

# ### Normal mode relaxation in small displacement approximation
Ph678 = js.dL()
for NN in [6,7,8]:
   Ph = js.bio.intScatFuncPMode(nm, NN, output=0, qlist=Deff.X)
   Ph678.append(Ph)

# ## effective diffusion Deff in initial slope (compare to cumulant fit)
a=100.
rate = 1/30000 # 1/ps
for Ph in Ph678:
   d = Deff.interp(Ph.X) + rate * a**2 * Ph._Pn / (Ph._Fq+a**2*Ph._Pn) / Ph.X**2
   p.Plot(Ph.X,1e5*d ,li='', le=f'rigid ADH + mode {Ph.modeNumber}  rmsd={Ph.kTrmsd*a:.2f} A')

p.Title('Alcohol dehydrogenase (ADH) effective diffusion \nwith additional normal mode relaxations')
p.Legend(x=1.5,y=5.5)
# p.savefig(js.examples.imagepath+'/ADHNM_Deff.jpg', dpi=100)

# Assume a common relaxation on top of diffusion
# that we add to  Deff
u.qlist = np.r_[0.2:2:0.2]    # [1/nm]
u.tlist = np.r_[1, 10:1e5:50]  # [ps]
Iqt = js.bio.intScatFuncYlm(u.residues,Dtrans=Dt,Drot=Dr,cubesize=1,getVolume='once')

# ### dynamic mode formfactor P() and relaxation in small displacement approximation with amplitude A(Q)
sumP = Ph678.Y.array.sum(axis=0)
def Aq(a):
    # NM mode formfactor amplitude sum
    aq = a**2*sumP / (Ph678[0]._Fq + a**2*sumP)
    return js.dA(np.c_[Ph678[0].X, aq].T)

p2=js.mplot()
p2.Yaxis(min=0.01, max=1, label='I(Q,t)/I(Q,0)')
p2.Xaxis(min=0, max=100000, label='t / ps')

Iqt2 = Iqt.copy()
l=1/10000  # 1/ps
Aqa = Aq(a)
for i, qt in enumerate(Iqt2):
    diff = qt.Y *(1-Aqa.interp(qt.q))
    qt.Y = qt.Y *((1-Aqa.interp(qt.q)) + Aqa.interp(qt.q)*np.exp(-l*qt.X))
     
    p2.Plot(qt.X, qt.Y * 0.8**i,sy=0,li=[3,2,i+1],le=f'{qt.q:.1f}')
    p2.Plot(qt.X, diff* 0.8**i,sy=0,li=[1,2,i+1])
    
p2.Yaxis(min=0.001,max=1,label='I(Q,t)/I(Q,0)',scale='log')
p2.Xaxis(min=0.1,max=100000,label='t / ps')
p2.Title('Intermediate scattering function with/without NM relaxation')
p2.Subtitle('scaled for visibility')
p2.Legend()
# p2.savefig(js.examples.imagepath+'/ADHNM_Iqt.jpg', dpi=100)

if 0 :
    # look at A(Q)
    p1=js.mplot()
    Aqa = Aq(a)
    p1.Plot(Aqa, sy=0, li=1)
    p1.Yaxis(min=0, max=0.8)

