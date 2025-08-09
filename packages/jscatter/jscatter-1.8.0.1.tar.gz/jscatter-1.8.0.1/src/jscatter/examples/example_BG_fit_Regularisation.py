import numpy as np
import jscatter as js

# data to fit
# We can fit all as it is faster than bayes
i5 = js.dL(js.examples.datapath+'/iqt_1hho.dat')

# model
def diffusion(A, D, t, elastic, wavevector=0):
    return A*np.exp(-wavevector**2*D*t) + elastic

# Define regularisation function that describes knowledge about the data, parameters or how parameters are distributed.
Amean, Asig = 1.0 , 0.01
Dmean, Dsig = 0.09 , 0.02
def ln_priorGAUSS(A, D):
    # assuming a normalised Gaussian distribution around the mean of A and D with width sig (Gaussian prior)
    # the log of the Gaussian is ~ lambda*w**2 = 0.5/Asig**2 * (a-Amean)**2,
    # lambda*w**2 should be always positive without normalisation.
    # the parameters are arrays for all elements of the dataList or a float for common parameters
    # the 't' is not included as it describes the .X values, 'elastic' is not used (no knowledge about it).
    lp = 0.5 * np.sum((A-Amean)**2/Asig**2)
    lp += 0.5 * np.sum((D-Dmean)**2/Dsig**2)
    return lp

# as example => Laplace prior.
# The Laplace prior has fatter tails than the Gaussian, and is also more concentrated around zero.
def ln_priorLAPLACE(A, D):
    # while Gauss uses L2 norm , here we use L1 norm =>|A-Amean|
    lp =  np.sum(np.abs(A-Amean)/(2**0.5*Asig))
    lp += np.sum(np.abs(D-Dmean)/2**0.5*Dsig)
    return lp

# as example => Gaussian around the average only for A and usage of current modelValues.
# if ln_prior has keyword 'modelValues' these are added from the current calculation
def ln_priorMEAN(modelValues, A):
    # for a free A we want that these are within some sigma with unknown mean.
    lp =  np.sum(np.abs(A-np.mean(A))**2) / Asig**2
    # this is a stupid example as demonstration
    # e.g in SAXS it might be I0 or Rg that determine a penalty
    # that is not in the parameters but in the formfactor calculation
    lp += 0 if modelValues.Y[:5,0].mean > 0.9 else 10

    return lp


i5.setlimit(D=[0.05, 1], A=[0.5, 1.5])

# do the fit with regression constrain in  ''ln_prior''.
i5.fit(model=diffusion, freepar={'D': [0.2], 'A': 0.98}, fixpar={'elastic': 0.0},
      mapNames={'t': 'X', 'wavevector': 'q'}, condition=lambda a: a.X<90,
      method='lm', ln_prior=ln_priorGAUSS)

i5.showlastErrPlot()

p=js.grace()
p.plot(i5.q,i5.D,i5.D_err,le='To strong regularisation')

# The result is not good as the constraint on D is to much constraining the diffusion coefficient.
# Therefore the errors are large and the values to close to 0.09.
# better is simple 'lm' without constrain in this case. This was wrong knowledge!

i5.fit(model=diffusion, freepar={'D': [0.2], 'A': 0.98}, fixpar={'elastic': 0.0},
       mapNames={'t': 'X', 'wavevector': 'q'}, condition=lambda a: a.X<90,
       method='lm',output=False)
p.plot(i5.q,i5.D,i5.D_err,le='LevenbergMarquardt fit')
p.legend(x=0.1,y=0.13)
p.yaxis(min=0.05,max=0.15)



