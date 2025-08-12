import torch

class BayesErrorImageFeature(torch.autograd.Function):
	@staticmethod
	def forward(ctx, images, labels, embedding_model, bayes_error_calculator, batch_size = 128):
		# batch_size = 8  # You can make this configurable
		device = images.device
	
		all_embeddings = []
		with torch.no_grad():
			for i in range(0, images.size(0), batch_size):
				img_batch = images[i:i + batch_size]
				emb_batch = embedding_model(img_batch)
				all_embeddings.append(emb_batch)
			embeddings = torch.cat(all_embeddings, dim=0)
	
		ctx.save_for_backward(images, labels)
		ctx.embedding_model = embedding_model
		ctx.embedding_batch_size = batch_size  # store for backward
	
		# Compute error and grad
		with torch.enable_grad():
			embeddings = embeddings.detach().requires_grad_(True)
			normalized = embeddings / (embeddings.abs().max() + 1e-8)
			error = bayes_error_calculator(normalized, labels)
	
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
		embedding_grads = ctx.embedding_grads
		batch_size = ctx.embedding_batch_size
	
		image_grads_list = []
	
		with torch.enable_grad():
			for i in range(0, images.size(0), batch_size):
				img_batch = images[i:i + batch_size].detach().requires_grad_(True)
				emb_batch = embedding_model(img_batch)
	
				grad_batch = embedding_grads[i:i + batch_size]
	
				grad_imgs = torch.autograd.grad(
					outputs=emb_batch,
					inputs=img_batch,
					grad_outputs=grad_batch,
					retain_graph=False,
					create_graph=False
				)[0]
				image_grads_list.append(grad_imgs)
	
		image_grads = torch.cat(image_grads_list, dim=0)
	
		return image_grads, None, None, None  # matching input structure
