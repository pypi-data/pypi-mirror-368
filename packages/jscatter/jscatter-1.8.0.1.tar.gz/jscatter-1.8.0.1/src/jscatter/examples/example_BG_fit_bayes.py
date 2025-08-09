import numpy as np
import jscatter as js
import matplotlib.pyplot as plt
import corner

# data to fit
# We use each a subset to speed up the example
i5 = js.dL(js.examples.datapath+'/iqt_1hho.dat')[[3, 5]]

# model
def diffusion(A, D, t, elastic, wavevector=0):
    return A*np.exp(-wavevector**2*D*t) + elastic

# Define ln_prior that describes knowledge about the data, parameters or how parameters are distributed.
# The ln_prior is complemented by the limits as:
# 0 within limits and -inf outside limits (as log og  probability 1 in limits and 0 outside)
# Without prior only the limits are used (uninformative prior) that
# the prior is optional if you know something about the parameters.

# As the prior is a probability it should be normalised. On the other side, as in the examples,
# the normalisation constants result in constant offset dependent on sigma
# and will not influence the best fit result but chi2.

Amean, Asig = 1.0 , 0.01
Dmean, Dsig = 0.09 , 0.02
def ln_priorGAUSS(A, D):
    # assuming a normalised Gaussian distribution around the mean of A and D with width sig (Gaussian prior)
    # https://en.wikipedia.org/wiki/Normal_distribution
    # the log of the Gaussian is the log_prior, the second log is from the Gaussian normalisation
    # the parameters are arrays for all elements of the dataList or a float for common parameters
    # the 't' is not included as it describes the .X values, 'elastic' is not used (no knowledge about it).
    lp = -0.5 * np.sum((A-Amean)**2/Asig**2) - (0.5 * np.log(2*np.pi) + np.log(Asig)) * len(A)
    lp += -0.5 * np.sum((D-Dmean)**2/Dsig**2) - (0.5 * np.log(2*np.pi) + np.log(Dsig)) * len(D)
    return lp

# as example => Laplace prior.
# The Laplace prior has fatter tails than the Gaussian, and is also more concentrated around zero.
def ln_priorLAPLACE(A, D):
    # while Gauss uses L2 norm , here we use L1 norm =>|A-Amean|
    # https://en.wikipedia.org/wiki/Laplace_distribution
    lp = -  np.sum(np.abs(A-Amean)/(2**0.5*Asig)) + np.log(1/(2*2**0.5*Asig)*len(A))
    lp += - np.sum(np.abs(D-Dmean)/2**0.5*Dsig) + np.log(1/(2*2**0.5*Dsig)*len(D))
    return lp

i5.setlimit(D=[0.05, 1], A=[0.5, 1.5])

# do Bayesian analysis with the prior
i5.fit(model=diffusion, freepar={'D': [0.2], 'A': 0.98}, fixpar={'elastic': 0.0},
      mapNames={'t': 'X', 'wavevector': 'q'}, condition=lambda a: a.X<90,
       method='bayes', tolerance=20, bayesnsteps=1000, ln_prior=ln_priorGAUSS)

i5.showlastErrPlot()

# get sampler chain and examine results removing burn in time 2*tau
tau = i5.getBayesSampler().get_autocorr_time(tol=20)
flat_samples = i5.getBayesSampler().get_chain(discard=int(2*tau.max()), thin=1, flat=True)
labels = i5.getBayesSampler().parlabels

plt.ion()
fig = corner.corner(flat_samples, labels=labels, quantiles=[0.16, 0.5, 0.84], show_titles=True, title_fmt='.3f')
plt.show()
# fig.savefig(js.examples.imagepath+'/bayescorner_withprior.jpg')
