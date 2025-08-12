import numpy as np
from scipy.spatial.distance import cdist

# ===== NumPy Version of Bayes Error =====
def bayes_error_numpy(X, y, sigma, num_classes):
	"""
	Estimate Bayes error using a Gaussian similarity kernel.
	
	Args:
		X (np.ndarray): [N, D] feature matrix.
		y (np.ndarray): [N] class labels.
		sigma (float): kernel width.
		num_classes (int): number of distinct classes.
	
	Returns:
		np.ndarray: Bayes error estimates per sample.
	"""
	N = X.shape[0]
	dists_sq = cdist(X, X, 'sqeuclidean')
	sims = np.exp(-dists_sq / (2 * sigma ** 2))
	np.fill_diagonal(sims, 0)  # Remove self-similarity
	
	Z = sims.sum(axis=1, keepdims=True)
	posteriors = np.zeros((N, num_classes))
	for c in range(num_classes):
		mask = (y == c).astype(np.float32)
		posteriors[:, c] = (sims * mask[None, :]).sum(axis=1) / (Z.squeeze() + 1e-8)
	
	return 1.0 - np.max(posteriors, axis=1)
