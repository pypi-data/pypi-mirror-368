import torch

def bayes_error_grad_torch(X, y, sigma, num_classes):
	"""
	Compute gradient of Bayes error w.r.t. X using autograd (Torch version).
	
	Args:
		X: [N, D] torch.Tensor (requires_grad=True)
		y: [N] torch.Tensor of labels
		sigma: scalar
		num_classes: number of classes
	
	Returns:
		torch.Tensor: gradient of shape [N, D]
	"""
	X = X.clone().detach().requires_grad_(True)
	dists_sq = torch.cdist(X, X, p=2).pow(2)
	sims = torch.exp(-dists_sq / (2 * sigma ** 2))
	# sims.fill_diagonal_(0)
	sims = sims - torch.diag_embed(torch.diagonal(sims))
	
	
	Z = sims.sum(dim=1, keepdim=True) + 1e-8
	posteriors = torch.zeros(X.size(0), num_classes, device=X.device)
	
	for c in range(num_classes):
		class_mask = (y == c).float().unsqueeze(0)  # [1, N]
		posteriors[:, c] = (sims * class_mask).sum(dim=1) / Z.squeeze(1)
	
	losses = 1.0 - posteriors.max(dim=1).values
	loss = losses.sum()
	loss.backward()
	
	return X.grad.detach()
