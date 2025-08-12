import torch

def bayes_error_torch(X, y, sigma, num_classes, batch_size=512):
	N, D = X.size()
	device = X.device
	
	posteriors = torch.zeros(N, num_classes, device=device)
	
	for start in range(0, N, batch_size):
		end = min(start + batch_size, N)
		X_batch = X[start:end]  # [B, D]
	
		# Compute dot product similarity between batch and full set
		dot_products = X_batch @ X.T  # [B, N]
		sims = torch.sigmoid(dot_products)  # [B, N]
	
		# Zero out self-similarity for in-batch indices
		# if end - start == N:
		# 	sims.fill_diagonal_(0.0)  # full batch = full set
		# else:
		# sims[:, start:end] = sims[:, start:end] - torch.diag_embed(torch.diagonal(sims[:, start:end]))
		mask = torch.ones_like(sims)
		rows = torch.arange(end - start)
		# print(mask.shape)
		# print(rows)
		cols = start + rows
		mask[rows, cols] = 0
		sims = sims * mask
	
		Z = sims.sum(dim=1, keepdim=True) + 1e-8  # [B, 1]
	
		for c in range(num_classes):
			class_mask = (y == c).float().unsqueeze(0)  # [1, N]
			class_sims = sims * class_mask  # [B, N]
			posteriors[start:end, c] = class_sims.sum(dim=1) / Z.squeeze(1)
	
	return 1.0 - posteriors.max(dim=1).values  # [N]
