import jscatter as js
import numpy as np

bi0 = js.dA(js.examples.datapath + '/bicelleDMPC-DHCP_5mg.csv', replace={',': ' '})


def bi(q, R, dR, tail, head, stail=290, shead=420, p=1, A=1, bgr=0, di=0.1):
    # bicelle model with an interface between tail/head and head/solvent
    # tail, head : float , thickness of layer
    # shead, stail : float SDL of layer in electron density unis (e/nm^3)
    sld = np.r_[stail, shead] * js.formel.felectron  # DPPC SAXS
    rim = np.r_[tail, head]
    solventSLD = 334 * js.formel.felectron
    # tail, head layers with interface regions of dd thickness
    sldp = np.r_[stail, (stail + shead) / 2, shead, (shead + solventSLD) / 2] * js.formel.felectron

    bicelle = js.ff.multiShellBicelle(q, R=R, shellthickness=[tail, di, head, di],
                                      rimthickness=[tail, di, head, di],
                                      p=p, dR=dR, shellSLD=sldp, rimSLD=sldp, solventSLD=solventSLD)

    # add background and scaling
    bicelle.Y = A * bicelle.Y + bgr
    return bicelle


free0 = {'R': 1.58, 'tail': 1.47, 'head': 0.37, 'shead': 460, 'stail': 292, 'A': 1933, 'bgr': 0.0001, 'dR': 0.5}
fix = {'p': 1, 'di': 0.1}
free = free0.copy()

#bi0.eY[bi0.X>0.89] *= 2
bi0.makeErrPlot(xscale='log', yscale='log')
bi0.setlimit(head=[0, 1.5], tail=[0, 3], R=[1, 6], shead=[350, 540], stail=[250, 320], dR=[0, 0.7], bgr=[0, 0.002],
             A=[0, None, 0])

bi0.setlimit(p=[1, 5, 0.99], hr=[0, 1])
bi0.fit(bi, free, fix, {'q': 'X'}, condition=lambda a: a.X > 0.3),  # method='diff',workers=12)
bi0.errPlotTitle(bi0.name.split('/')[-1].split('.')[0])
bi0.errplot.legend(x=1,y=0.002)

# bi0.savelastErrPlot(js.examples.imagepath+'/interfacialBicelle.jpg',size=[2,2])