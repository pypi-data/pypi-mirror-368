# -*- coding: utf-8 -*-
#  this file is intended to be used in the debugger
# write a script that calls your function to debug it

import numpy as np
import jscatter as js

import jscatter as js
import numpy as np
uni=js.bio.scatteringUniverse('1igt')
uni.qlist=np.r_[0.025:1.5:0.1]
uni.tlist = np.r_[1:20000:20j,20000:100000:20j]

# rigid protein trans/rot diffusion
hR = js.bio.hullRad(uni.atoms)
Dtrans = hR['Dt'] * 1e2  # in nm²/ps
Drot = hR['Dr'] * 1e-12  # in 1/ps
Iqt = js.bio.intScatFuncYlm(uni.residues, Dtrans=Dtrans, Drot=Drot)

# internal domain motions
bnm = js.bio.brownianNMdiag(uni.residues, k_b=70, f_d=500)
# 1/iRT = 12 000 ps for f_d = 0.2

OU = js.bio.intScatFuncOU(bnm, [6, 7, 8], cubesize=2)


# combine diffusion and internal dynamics
IqtOU = Iqt.copy()
for i, iqtou in enumerate(IqtOU):
    ou = OU.filter(q=iqtou.q)[0]
    # combining in this case its just multiplication in time domain
    iqtou.Y = iqtou.Y * ou.Y

# show the result comparing the contributions
p=js.grace(2,0.8)
p.multi(1, 3, hgap=0)
p[0].plot(Iqt, li=-1)
p[1].plot(OU, li=-1)
p[2].plot(IqtOU, sy=[1,0.3,-1], li=-1)
for i in [0,1,2]:
    p[i].xaxis(label=r'\xt\f{} / ps', min=0, max=100000, charsize=1.5)
    p[i].yaxis(scale='log', min=0.01, max=1)
p[0].yaxis(label='I(Q,t)/I(Q,0)', charsize=1.5)
p[0].subtitle('trans/rot diffusion', size=1.5)
p[1].subtitle('internal dynamics', size=1.5)
p[2].subtitle('trans/rot diffusion + internal dynamics',size=1.5)
p[1].title('friction dominated internal dynamics in harmonic potential',size=2)
# p.save(js.examples.imagepath+'/iqtOrnsteinUhlenbeck.jpg',size=(1000/300,400/300))














