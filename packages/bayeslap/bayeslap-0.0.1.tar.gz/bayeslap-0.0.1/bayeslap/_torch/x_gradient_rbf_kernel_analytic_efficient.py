import torch
from tqdm import trange

def bayes_error_grad_torch(X, y, sigma, num_classes, chunk_size=512):
    N, D = X.shape
    sigma_sq = sigma ** 2
    grads = torch.zeros_like(X)
    
    for start in trange(0, N, chunk_size):
        end = min(start + chunk_size, N)
        X_chunk = X[start:end]  # [B, D]
        # y_chunk = y[start:end]  # [B]
        B = X_chunk.shape[0]

        # Pairwise distances: [B, N]
        dists_sq = torch.cdist(X_chunk, X).pow(2)
        sims = torch.exp(-dists_sq / (2 * sigma_sq))  # [B, N]
        # sims[:, start:end] = 0  # zero diagonal for current chunk
        mask = torch.ones_like(sims)
        rows = torch.arange(end - start)
        # print(mask.shape)
        # print(rows)
        cols = start + rows
        mask[rows, cols] = 0
        sims = sims * mask

        Z = sims.sum(dim=1, keepdim=True) + 1e-8  # [B, 1]

        # Compute posteriors: [B, C]
        posteriors = torch.zeros(B, num_classes, device=X.device)
        for c in range(num_classes):
            mask = (y == c).float()  # [N]
            posteriors[:, c] = (sims * mask).sum(dim=1) / Z.squeeze(1)

        y_max = torch.argmax(posteriors, dim=1)  # [B]
        label_match = (y.unsqueeze(0) == y_max.unsqueeze(1)).float()  # [B, N]

        N_yhat = (sims * label_match).sum(dim=1)  # [B]
        coeff = ((label_match * Z) - N_yhat[:, None]) / (Z ** 2)  # [B, N]

        # Pairwise diffs: [B, N, D]
        diff = (X_chunk[:, None, :] - X[None, :, :]) / sigma_sq  # [B, N, D]
        grad_contrib = coeff.unsqueeze(2) * sims.unsqueeze(2) * diff  # [B, N, D]

        # Accumulate grads for X_chunk
        grads[start:end] += grad_contrib.sum(dim=1)  # [B, D]

        # Also subtract transposed contributions to grad[j]
        grads -= grad_contrib.sum(dim=0)  # [N, D]
    
    return grads
