import torch
from torch.autograd import Function

class BayesErrorRBF(Function):
	@staticmethod
	def forward(ctx, X, y, sigma, num_classes, chunk_size=512):
		N, D = X.shape
		sigma_sq = sigma ** 2
		grads = torch.zeros_like(X)
		posteriors = torch.zeros(N, num_classes, device=X.device)
	
		for start in range(0, N, chunk_size):
			end = min(start + chunk_size, N)
			X_chunk = X[start:end]
			B = end - start
	
			dists_sq = torch.cdist(X_chunk, X).pow(2)  # [B, N]
			sims = torch.exp(-dists_sq / (2 * sigma_sq))  # [B, N]
	
			# Mask diagonal
			mask = torch.ones_like(sims)
			rows = torch.arange(B, device=X.device)
			cols = start + rows
			mask[rows, cols] = 0
			sims = sims * mask
	
			Z = sims.sum(dim=1, keepdim=True) + 1e-8  # [B, 1]
	
			for c in range(num_classes):
				class_mask = (y == c).float()
				posteriors[start:end, c] = (sims * class_mask).sum(dim=1) / Z.squeeze(1)
	
			y_max = torch.argmax(posteriors[start:end], dim=1)
	
			# Compute gradient
			label_match = (y.unsqueeze(0) == y_max.unsqueeze(1)).float()  # [B, N]
			N_yhat = (sims * label_match).sum(dim=1)  # [B]
			coeff = ((label_match * Z) - N_yhat[:, None]) / (Z ** 2)  # [B, N]
	
			diff = (X_chunk[:, None, :] - X[None, :, :]) / sigma_sq  # [B, N, D]
			grad_contrib = coeff.unsqueeze(2) * sims.unsqueeze(2) * diff  # [B, N, D]
	
			grads[start:end] += grad_contrib.sum(dim=1)
			grads -= grad_contrib.sum(dim=0)
	
		ctx.save_for_backward(grads)
		return (1.0 - posteriors.max(dim=1).values).mean()
	
	@staticmethod
	def backward(ctx, grad_output):
		(grads,) = ctx.saved_tensors
		return grad_output * grads, None, None, None, None
