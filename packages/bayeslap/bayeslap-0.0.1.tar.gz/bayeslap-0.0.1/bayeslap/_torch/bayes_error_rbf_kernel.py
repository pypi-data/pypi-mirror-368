import torch

def bayes_error_torch(X, y, sigma, num_classes):
	"""
	Estimate Bayes error using a Gaussian similarity kernel (Torch version).
	
	Args:
		X (torch.Tensor): [N, D] feature matrix.
		y (torch.Tensor): [N] class labels.
		sigma (float): kernel width.
		num_classes (int): number of distinct classes.
	
	Returns:
		torch.Tensor: Bayes error estimates per sample. Shape: [N]
	"""
	N = X.size(0)
	dists_sq = torch.cdist(X, X, p=2).pow(2)  # shape: [N, N]
	sims = torch.exp(-dists_sq / (2 * sigma ** 2))  # Gaussian kernel
	# sims.fill_diagonal_(0)  # Remove self-similarity
	sims = sims - torch.diag_embed(torch.diagonal(sims))
	
	Z = sims.sum(dim=1, keepdim=True) + 1e-8
	posteriors = torch.zeros(N, num_classes, device=X.device)
	
	for c in range(num_classes):
		class_mask = (y == c).float().unsqueeze(0)  # [1, N]
		posteriors[:, c] = (sims * class_mask).sum(dim=1) / Z.squeeze(1)
	
	return 1.0 - posteriors.max(dim=1).values
