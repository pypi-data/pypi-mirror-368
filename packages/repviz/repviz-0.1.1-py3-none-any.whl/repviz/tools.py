from typing import Union

import torch
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


def gram_linear(x):
    return x @ x.T


def center_gram(gram, unbiased=False):
    if not np.allclose(gram, gram.T):
        raise ValueError("Input must be a symmetric matrix.")
    gram = gram.copy()

    if unbiased:
        n = gram.shape[0]
        np.fill_diagonal(gram, 0)
        means = np.sum(gram, 0, dtype=np.float64) / (n - 2)
        means -= np.sum(means) / (2 * (n - 1))
        gram -= means[:, None]
        gram -= means[None, :]
        np.fill_diagonal(gram, 0)
    else:
        means = np.mean(gram, 0, dtype=np.float64)
        means -= np.mean(means) / 2
        gram -= means[:, None]
        gram -= means[None, :]

    return gram


def cka(gram_x, gram_y, debiased=False):
    gram_x = center_gram(gram_x, unbiased=debiased)
    gram_y = center_gram(gram_y, unbiased=debiased)

    scaled_hsic = gram_x.ravel().dot(gram_y.ravel())

    normalization_x = np.linalg.norm(gram_x)
    normalization_y = np.linalg.norm(gram_y)
    return scaled_hsic / (normalization_x * normalization_y)


def decomposition(
    mat: Union[torch.Tensor, np.ndarray], n_components: int, method: str = "PCA"
) -> np.ndarray:
    if isinstance(mat, torch.Tensor):
        mat = np.array(mat)

    decomposer = (
        PCA(n_components=n_components)
        if method == "PCA"
        else TSNE(n_components=n_components)
    )
    decomposed_mat = decomposer.fit_transform(mat)

    return decomposed_mat
