import numpy as np
#import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from sklearn.mixture import GaussianMixture as GMM
from scipy import linalg

def confidence_ellipse(X, ax, n_std=3.0, facecolor='none', **kwargs):
	"""
	Create a plot of the confidence ellipse using the new method.

	Parameters
	----------
	X : array-like, shape (n, 2)
		Input data points.

	ax : matplotlib.axes.Axes
		The axes object to draw the ellipse into.

	n_std : float
		The number of standard deviations to determine the ellipse's radiuses.

	**kwargs
		Forwarded to `~matplotlib.patches.Ellipse`
	"""

	# Step 1: Fit a 1-component GMM
	gmm = GMM(n_components=1, covariance_type='full').fit(X)
	
	# Step 2: Extract parameters
	xc, yc = gmm.means_[0]  # Center of the ellipse (x_c, y_c)
	covariance = gmm.covariances_[0]  # Covariance matrix

	# Step 3: Calculate the eigenvalues and eigenvectors of the covariance matrix
	eigenvalues, eigenvectors = linalg.eigh(covariance)

	# Sort the eigenvalues and eigenvectors
	order = eigenvalues.argsort()[::-1]
	eigenvalues, eigenvectors = eigenvalues[order], eigenvectors[:, order]

	# Width and height of ellipse (according to n_std)
	a, b = n_std * np.sqrt(eigenvalues)  # Major and minor axes

	# Angle of ellipse (radians)
	theta = np.arctan2(*eigenvectors[:, 0][::-1])
		
	# Create an ellipse patch
	ellipse = Ellipse((xc, yc), width=2*a, height=2*b, angle=np.degrees(theta),
					  facecolor=facecolor, **kwargs)
	# Add the ellipse to the axes
	ax.add_patch(ellipse)
	
	# Return the average per-sample log-likelihood of the data X
	return gmm



