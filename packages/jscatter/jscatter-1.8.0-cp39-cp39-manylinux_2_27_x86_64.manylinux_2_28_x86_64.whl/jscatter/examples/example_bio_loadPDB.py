import jscatter as js
import numpy as np

uni = js.bio.scatteringUniverse('3rn3')
uni.view()
uni.setSolvent('1d2o1')
uni.qlist = js.loglist(0.1, 5, 100)
# calc scattering both here in D2O
S = js.bio.nscatIntUniv(uni.select_atoms('protein'))
S = js.bio.xscatIntUniv(uni.select_atoms('protein'))

p = js.grace()
p.title('N scattering solvent matching')
p.yaxis(scale='l', label=r'I(Q) / nm\S2\N/particle')
p.xaxis(scale='l', label='Q / nm\S-1')

for x in np.r_[0:0.5:0.1]:
    uni.setSolvent([f'{x:.2f}d2o1',f'{1-x:.2f}h2o1' ])
    Sn = js.bio.nscatIntUniv(uni.select_atoms('protein'))
    p.plot(Sn, le=f'{x:.2f} D2O')

p.legend()
# p.save(js.examples.imagepath+'/biosolventmatching.jpg', size=(2, 2))
