import torch
import torch.nn.functional as F
from tqdm import trange


def bayes_error_grad(X, y, num_classes, chunk_size=512):
	N, D = X.shape
	grads = torch.zeros_like(X)
	
	for start in trange(0, N, chunk_size):
		end = min(start + chunk_size, N)
		X_chunk = X[start:end]  # [B, D]
		y_chunk = y[start:end]  # [B]
		B = X_chunk.shape[0]
	
		# Dot products: [B, N]
		dot_products = X_chunk @ X.T  # [B, N]
		sims = torch.sigmoid(dot_products)  # [B, N]
		# sims[:, start:end] = 0  # remove self-similarity
		mask = torch.ones_like(sims)
		rows = torch.arange(end - start)
		# print(mask.shape)
		# print(rows)
		cols = start + rows
		mask[rows, cols] = 0
		sims = sims * mask
	
		Z = sims.sum(dim=1, keepdim=True) + 1e-8  # [B, 1]
	
		# Posteriors: [B, C]
		posteriors = torch.zeros(B, num_classes, device=X.device)
		for c in range(num_classes):
			mask = (y == c).float()  # [N]
			posteriors[:, c] = (sims * mask).sum(dim=1) / Z.squeeze(1)
	
		y_max = torch.argmax(posteriors, dim=1)  # [B]
		label_match = (y.unsqueeze(0) == y_max.unsqueeze(1)).float()  # [B, N]
		N_yhat = (sims * label_match).sum(dim=1)  # [B]
		coeff = ((label_match * Z) - N_yhat[:, None]) / (Z ** 2)  # [B, N]
	
		sim_deriv = sims * (1 - sims)  # [B, N]
		mult = coeff * sim_deriv  # [B, N]
	
		# grad_i = mult @ X  → grad for this chunk
		grad_i = mult @ X  # [B, D]
		grads[start:end] -= grad_i  # apply -grad_i
	
		# grad_j = mult.T @ X_chunk  → contributions to full grads from this chunk
		grad_j = mult.T @ X_chunk  # [N, D]
		grads -= grad_j  # apply -grad_j
	
	return grads
