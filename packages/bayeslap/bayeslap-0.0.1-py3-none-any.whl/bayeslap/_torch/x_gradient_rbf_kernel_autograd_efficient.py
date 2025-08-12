from tqdm import tqdm
import torch

def bayes_error_grad_torch(X, y, sigma, num_classes, chunk_size=64):
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
	N = X.size(0)
	grads = torch.zeros_like(X)
	
	X = X.clone().detach().requires_grad_(True)
	# dists_sq = torch.cdist(X, X, p=2).pow(2)
	
	for start in tqdm(range(0, N, chunk_size), desc="Batched"):
		end = min(start + chunk_size, N)
		chunk = X[start:end]  # [B, D]
		dists = torch.cdist(chunk, X, p=2)  # [B, N]
	
		sims = torch.exp(-dists.pow(2) / (2 * sigma ** 2))
		# sims.fill_diagonal_(0)
		# sims = sims - torch.diag_embed(torch.diagonal(sims))
		# Safe masking to zero out self-similarity within batch
		mask = torch.ones_like(sims)
		rows = torch.arange(end - start)
		# print(mask.shape)
		# print(rows)
		cols = start + rows
		mask[rows, cols] = 0
		sims = sims * mask
	
	
		Z = sims.sum(dim=1, keepdim=True) + 1e-8
		# posteriors = torch.zeros(X.size(0), num_classes, device=X.device)
		posteriors = torch.zeros(end - start, num_classes, device=X.device)
	
		for c in range(num_classes):
			class_mask = (y == c).float().unsqueeze(0)  # [1, N]
			posteriors[:, c] = (sims * class_mask).sum(dim=1) / Z.squeeze(1)
	
		losses = 1.0 - posteriors.max(dim=1).values
		loss = losses.sum()
		# loss.backward()
	
		# loss = (1 - posteriors.max(dim=1)[0]).mean()
		loss.backward(retain_graph=True)
	
		# grads[start:end] = X.grad[start:end]
		# X.grad[start:end].zero_()
		grads += X.grad
		X.grad.zero_()
	
	return grads
