import jscatter as js

data = js.dL(js.examples.datapath + '/iqt_1hho.dat')
# make plot with size 2,3
p = js.grace(3, 2)
# plot data
# symbol -1 changes in color and type is equivalent to [-1,0.3,-1] , here -1 change for consecutive sets
# line is type 1,thickness 1 and '' syncs
# legend '$q'  takes the value of the parameter q from the data like in a shell
p.plot(data, symbol=-1, line=[1, 1, ''], legend='q=$q')
# make axes
p.yaxis(min=0.09, max=1.1, scale='l', label='I(Q,t)/I(Q,0)', charsize=1.50)
p.xaxis(min=0.0, max=250, label='fouriertime t / ns ', charsize=1.50)
# place legend, title, and subtitle
p.legend(x=190, y=1)
p.title('An example for the intermediate scattering function in Neutron Spinecho Spectroscopy', size=1)
p.subtitle('colors of line are sync to symbol color')
# add a text
p.text(r'Here we place a text just as demo\n at the last point of this dataset', x=90, y=0.18, charsize=1)
p.save('grace0_newsimplestyle.png')
