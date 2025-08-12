import torch
import torch.nn.functional as F

def bayes_error_grad_dot_sigmoid(X, y, num_classes):
	N, D = X.shape
	
	# Compute pairwise dot products
	dot_products = X @ X.T  # [N, N]
	sims = torch.sigmoid(dot_products)  # [N, N]
	sims.fill_diagonal_(0)
	
	Z = sims.sum(dim=1, keepdim=True) + 1e-8  # [N, 1]
	
	# Posteriors
	posteriors = torch.zeros(N, num_classes, device=X.device)
	for c in range(num_classes):
		mask = (y == c).float()
		posteriors[:, c] = (sims * mask).sum(dim=1) / Z.squeeze(1)
	
	y_max = torch.argmax(posteriors, dim=1)  # [N]
	label_match = (y.unsqueeze(0) == y_max.unsqueeze(1)).float()  # [N, N]
	N_yhat = (sims * label_match).sum(dim=1)  # [N]
	coeff = ((label_match * Z) - N_yhat[:, None]) / (Z ** 2)  # [N, N]
	
	# Compute gradient of similarity wrt X
	sim_deriv = sims * (1 - sims)  # [N, N]
	mult = coeff * sim_deriv  # [N, N]
	
	# grads[i] += sum_j mult[i,j] * X[j]
	grad_i = mult @ X  # [N, D]
	# grads[j] += sum_i mult[i,j] * X[i]
	grad_j = mult.T @ X  # [N, D]
	
	return - grad_i - grad_j  # total gradient for each X[i]
