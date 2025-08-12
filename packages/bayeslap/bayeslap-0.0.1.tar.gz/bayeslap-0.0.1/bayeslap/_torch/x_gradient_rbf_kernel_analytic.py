import torch

def bayes_error_grad_torch_manual(X, y, sigma, num_classes):
	N, D = X.shape
	sigma_sq = sigma ** 2
	grads = torch.zeros_like(X)
	
	dists_sq = torch.cdist(X, X).pow(2)  # [N, N]
	sims = torch.exp(-dists_sq / (2 * sigma_sq))  # [N, N]
	sims.fill_diagonal_(0)
	
	Z = sims.sum(dim=1, keepdim=True) + 1e-8  # [N, 1]
	posteriors = torch.zeros(N, num_classes, device=X.device)
	
	for c in range(num_classes):
		mask = (y == c).float().unsqueeze(0)  # [1, N]
		posteriors[:, c] = (sims * mask).sum(dim=1) / Z.squeeze(1)
	
	y_max = torch.argmax(posteriors, dim=1)
	
	# Compute full gradient: accumulate contributions to all points
	for i in range(N):
		Z_i = Z[i, 0]
		yhat_i = y_max[i]
		N_yhat = sims[i, y == yhat_i].sum()
	
		for j in range(N):
			if i == j:
				continue
			s_ij = sims[i, j]
			indicator = 1.0 if y[j] == yhat_i else 0.0
			coeff = (indicator * Z_i - N_yhat) / (Z_i ** 2)
			diff = (X[i] - X[j]) / sigma_sq
	
			grads[i] += coeff * s_ij * diff  # ∂loss[i]/∂X[i]
			grads[j] -= coeff * s_ij * diff  # ∂loss[i]/∂X[j] ← added term
	
	return grads
