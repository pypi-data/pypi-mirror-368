import jscatter as js

# TeubnerStrey model for micro emulsions

q = js.loglist(0.1, 5, 200)
p = js.grace()
for d, xi in zip([20, 10, 10, 10, 10], [20, 20, 10, 4, 1]):
    TB = js.ff.teubnerStrey(q, xi, d, eta2=1)
    p.plot(TB, symbol=0, line=[1, 2, -1], legend='d=%.2g xi=%.2g' % (d, xi))
p.yaxis(max=10000, min=1e-3, scale='l', label='I(Q)', charsize=1.5)
p.xaxis(min=0.1, max=5, scale='l', label=r'Q / nm\S-1', charsize=1.5)
p.legend(x=0.2, y=1)
p.title('Teubner Strey model for microemulsions')
p.save('TeubnerStrey.png')
