import numpy as np
import jscatter as js

# Hydrodynamic function and structure factor of hard spheres
# The hydrodynamic function describes how diffusion of spheres in concentrated suspension
# is changed due to hydrodynamic interactions.
# The diffusion is changed according to D(Q)=D0*H(Q)/S(Q)
# with the hydrodynamic function H(Q), structure factor S(Q)
# and Einstein diffusion of sphere D0

# some  wavevectors
q = np.r_[0:5:0.03]

p = js.grace(2, 1.5)
p.multi(1, 2)
p[0].title('Hydrodynamic function H(Q)')
p[0].subtitle('concentration dependence')
Rh = 2.2
for ii, mol in enumerate(np.r_[0.1:20:5]):
    H = js.sf.hydrodynamicFunct(q, Rh, molarity=0.001 * mol, )
    p[0].plot(H, sy=[1, 0.3, ii + 1], legend='H(Q) c=%.2g mM' % mol)
    p[0].plot(H.X, H[3], sy=0, li=[1, 2, ii + 1], legend='structure factor')

p[0].legend(x=2, y=2.4)
p[0].yaxis(min=0., max=2.5, label='S(Q); H(Q)')
p[0].xaxis(min=0., max=5., label=r'Q / nm\S-1')

# hydrodynamic function and structure factor of charged spheres
p[1].title('Hydrodynamic function H(Q)')
p[1].subtitle('screening length dependence')
for ii, scl in enumerate(np.r_[0.1:30:6]):
    H = js.sf.hydrodynamicFunct(q, Rh, molarity=0.0005, structureFactor=js.sf.RMSA,
                                structureFactorArgs={'R': Rh * 2, 'scl': scl, 'gamma': 5}, )
    p[1].plot(H, sy=[1, 0.3, ii + 1], legend='H(Q) scl=%.2g nm' % scl)
    p[1].plot(H.X, H[3], sy=0, li=[1, 2, ii + 1], legend='structure factor')

p[1].legend(x=2, y=2.4)
p[1].yaxis(min=0., max=2.5, label='S(Q); H(Q)')
p[1].xaxis(min=0., max=5., label=r'Q / nm\S-1')

p[0].text(r'high Q shows \nreduction in D\sself', x=3, y=0.22)
p[1].text(r'low Q shows reduction \ndue to stronger interaction', x=0.5, y=0.25)

p.save('HydrodynamicFunction.png')
