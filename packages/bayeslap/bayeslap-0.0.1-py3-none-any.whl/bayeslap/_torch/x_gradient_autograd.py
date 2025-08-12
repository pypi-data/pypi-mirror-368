def bayes_error_grad_torch_autograd(f, X, y, sigma, num_classes):
	X = X.clone().detach().requires_grad_(True)
	losses = f(X, y, sigma, num_classes)
	loss = losses.sum()
	loss.backward()
	return X.grad.detach()
