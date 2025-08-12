import torch

def bayes_error_torch(X, y, sigma, num_classes):
	
	N = X.size(0)
	
	# Similarity: sigmoid(dot product)
	dot_products = X @ X.T  # [N, N]
	sims = torch.sigmoid(dot_products)  # [N, N]
	sims = sims - torch.diag_embed(torch.diagonal(sims))  # zero self-similarity
	
	Z = sims.sum(dim=1, keepdim=True) + 1e-8  # normalization
	
	posteriors = torch.zeros(N, num_classes, device=X.device)
	for c in range(num_classes):
		class_mask = (y == c).float().unsqueeze(0)  # [1, N]
		posteriors[:, c] = (sims * class_mask).sum(dim=1) / Z.squeeze(1)
	
	return 1.0 - posteriors.max(dim=1).values  # [N]
