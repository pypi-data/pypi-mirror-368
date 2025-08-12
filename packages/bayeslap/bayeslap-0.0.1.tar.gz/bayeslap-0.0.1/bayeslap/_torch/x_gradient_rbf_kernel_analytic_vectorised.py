import torch

def bayes_error_grad_torch(X, y, sigma, num_classes):
	N, D = X.shape
	sigma_sq = sigma ** 2
	
	# Pairwise distances and similarities
	dists_sq = torch.cdist(X, X).pow(2)  # [N, N]
	sims = torch.exp(-dists_sq / (2 * sigma_sq))  # [N, N]
	sims.fill_diagonal_(0)
	
	Z = sims.sum(dim=1, keepdim=True) + 1e-8  # [N, 1]
	
	# Posteriors
	posteriors = torch.zeros(N, num_classes, device=X.device)
	for c in range(num_classes):
		mask = (y == c).float()  # [N]
		posteriors[:, c] = (sims * mask).sum(dim=1) / Z.squeeze(1)
	
	y_max = torch.argmax(posteriors, dim=1)  # [N]
	
	# Indicator matrix: [N, N], whether j matches y_max[i]
	label_match = (y.unsqueeze(0) == y_max.unsqueeze(1)).float()  # [N, N]
	
	# Sum of matching similarities: N_yhat[i] = sum_j sims[i, j] if y[j] == yhat[i]
	N_yhat = (sims * label_match).sum(dim=1)  # [N]
	coeff = ((label_match * Z) - N_yhat[:, None]) / (Z ** 2)  # [N, N]
	
	# Pairwise diffs: [N, N, D]
	diff = (X[:, None, :] - X[None, :, :]) / sigma_sq  # [N, N, D]
	grad_contrib = coeff.unsqueeze(2) * sims.unsqueeze(2) * diff  # [N, N, D]
	
	# Sum over j contributions to grad[i]
	grads = grad_contrib.sum(dim=1)  # [N, D]
	# Subtract transposed contributions to grad[j]
	grads -= grad_contrib.sum(dim=0)  # [N, D]
	
	return grads
