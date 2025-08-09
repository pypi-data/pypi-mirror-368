# How to build simple models
# which are actually not so simple....

import numpy as np
import jscatter as js

# Build models in one line using lambda
# directly calc the values and return only Y values
diffusion = lambda A, D, t, wavevector, elastic=0: A * np.exp(-wavevector ** 2 * D * t) + elastic

# use a model from the libraries
# here Teubner-Strey adding background and power law
# this returns as above only Y values
tbpower = lambda q, B, xi, dd, A, beta, bgr: js.ff.teubnerStrey(q=q, xi=xi, d=dd).Y * B + A * q ** beta + bgr


# The same as above in a function definition
# This should be the preferred way
def diffusion2(A, D, t, elastic, wavevector=0):
    Y = A * np.exp(-wavevector ** 2 * D * t) + elastic
    return Y


# returning dataArray allows additional attributes to be included in the result
# this returns a dataArray with X, Y values and attributes
# and is how Jscatter model return data
def diffusion3(A, D, t, wavevector, elastic=0):
    Y = A * np.exp(-wavevector ** 2 * D * t) + elastic
    result = js.dA(np.c_[t, Y].T)
    result.diffusioncoefficient = D
    result.wavevector = wavevector
    result.columnname = 'time;Iqt'
    return result


# supplement an existing model
def tbpower2(q, B, xi, dd, A, beta, bgr):
    """Model Teubner Strey  + power law and background"""
    # save different contributions for later analysis
    tb = js.ff.teubnerStrey(q=q, xi=xi, d=dd)
    pl = A * q ** beta  # power law
    tb = tb.addZeroColumns(2)
    tb[-2] = pl  # save power law in new last column
    tb[-1] = tb.Y  # save Teubner-Strey in last column
    tb.Y = B * tb.Y + pl + bgr  # put full model to Y values (usually tb[1])
    # save the additional parameters ; xi and d already included in teubnerStrey
    tb.A = A
    tb.bgr = bgr
    tb.beta = beta
    tb.columnname = 'q;Iq,IqTb,Iqpower'
    return tb

# How to add a numpy like docstring see in the example "How to build a complex model".
