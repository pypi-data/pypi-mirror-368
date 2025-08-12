import torch

class BayesErrorImageFeature(torch.autograd.Function):
	@staticmethod
	def forward(ctx, images, labels, embedding_model, bayes_error_calculator):
		with torch.no_grad():
			embeddings = embedding_model(images)
		ctx.save_for_backward(images, labels)
		ctx.embedding_model = embedding_model
	
		with torch.enable_grad():
			embeddings = embeddings.detach().requires_grad_(True)
			error = bayes_error_calculator(embeddings / embeddings.abs().max(), labels)
	
			grad_embeddings, = torch.autograd.grad(
				outputs=error,
				inputs=embeddings,
				grad_outputs=torch.ones_like(error),
				create_graph=False
			)
	
			ctx.embedding_grads = grad_embeddings
	
		return error
	
	@staticmethod
	def backward(ctx, grad_output):
		images, labels = ctx.saved_tensors
		embedding_model = ctx.embedding_model
	
		with torch.enable_grad():
	
	
			images = images.detach().requires_grad_(True)
			embeddings_from_input = embedding_model(images)
	
			image_grads = torch.autograd.grad(
				outputs=embeddings_from_input,
				inputs=images,
				grad_outputs=ctx.embedding_grads,
				create_graph=False,
				retain_graph=False,
				only_inputs=True
			)[0]
	
	
		return image_grads, None, None, None  # None for non-tensor inputs
