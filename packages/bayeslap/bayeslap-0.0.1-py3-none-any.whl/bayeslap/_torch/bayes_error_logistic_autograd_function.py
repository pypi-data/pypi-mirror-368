import torch
from torch.autograd import Function

class BayesErrorLogistic(Function):
	@staticmethod
	def forward(ctx, X, y, num_classes, chunk_size=512):
		N, D = X.shape
		grads = torch.zeros_like(X)
		posteriors = torch.zeros(N, num_classes, device=X.device)
	
		for start in range(0, N, chunk_size):
			end = min(start + chunk_size, N)
			X_chunk = X[start:end]  # [B, D]
			y_chunk = y[start:end]
			B = end - start
	
			dot_products = X_chunk @ X.T  # [B, N]
			sims = torch.sigmoid(dot_products)  # [B, N]
	
			# Zero diagonal
			mask = torch.ones_like(sims)
			rows = torch.arange(B, device=X.device)
			cols = start + rows
			mask[rows, cols] = 0
			sims = sims * mask
	
			Z = sims.sum(dim=1, keepdim=True) + 1e-8  # [B, 1]
	
			# Posteriors
			for c in range(num_classes):
				class_mask = (y == c).float()  # [N]
				posteriors[start:end, c] = (sims * class_mask).sum(dim=1) / Z.squeeze(1)
	
			y_max = torch.argmax(posteriors[start:end], dim=1)  # [B]
	
			label_match = (y.unsqueeze(0) == y_max.unsqueeze(1)).float()  # [B, N]
			N_yhat = (sims * label_match).sum(dim=1)  # [B]
			coeff = ((label_match * Z) - N_yhat[:, None]) / (Z ** 2)  # [B, N]
	
			sim_deriv = sims * (1 - sims)  # [B, N]
			mult = coeff * sim_deriv  # [B, N]
	
			grad_i = mult @ X  # [B, D]
			grads[start:end] -= grad_i
	
			grad_j = mult.T @ X_chunk  # [N, D]
			grads -= grad_j
	
		ctx.save_for_backward(grads)
		return (1.0 - posteriors.max(dim=1).values).mean()
	
	@staticmethod
	def backward(ctx, grad_output):
		(grads,) = ctx.saved_tensors
		return grad_output * grads, None, None, None
