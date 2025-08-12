import numpy as np

def bayes_error_grad_numpy(X, y, sigma, num_classes):
	"""
	Compute analytical gradient of Bayes error w.r.t. X (NumPy version, fully correct).
	Args:
		X: [N, D] array
		y: [N] array of labels
		sigma: float, kernel width
		num_classes: int, number of classes
	
	Returns:
		grad: [N, D] gradient array
	"""
	N, D = X.shape
	sigma_sq = sigma ** 2
	grad = np.zeros_like(X)
	
	# Pairwise squared distances and similarities
	dists_sq = np.sum((X[:, None, :] - X[None, :, :]) ** 2, axis=2)
	sims = np.exp(-dists_sq / (2 * sigma_sq))
	np.fill_diagonal(sims, 0)
	
	Z = sims.sum(axis=1, keepdims=True) + 1e-8  # [N, 1]
	posteriors = np.zeros((N, num_classes))
	
	for c in range(num_classes):
		class_mask = (y[None, :] == c).astype(float)  # [1, N]
		posteriors[:, c] = (sims * class_mask).sum(axis=1) / Z[:, 0]
	
	y_max = np.argmax(posteriors, axis=1)
	
	for i in range(N):
		Z_i = Z[i, 0]
		yhat_i = y_max[i]
		mask_yhat = (y == yhat_i).astype(float)
		N_yhat = np.sum(sims[i, :] * mask_yhat)
	
		for j in range(N):
			if i == j:
				continue
	
			sim_ij = sims[i, j]
			diff = X[i] - X[j]
			indicator = 1.0 if y[j] == yhat_i else 0.0
			coeff = (indicator * Z_i - N_yhat) / (Z_i ** 2)
			d_sim = sim_ij * diff / sigma_sq
	
			# Gradient w.r.t. X[i]
			grad[i] += coeff * d_sim
			# Gradient w.r.t. X[j] (symmetric, negative direction)
			grad[j] -= coeff * d_sim
	
	return grad
