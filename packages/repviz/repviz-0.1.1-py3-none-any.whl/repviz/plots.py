from typing import Dict, Optional, List, Union

import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from .tools import cka, gram_linear


def activation_scatter(
    activations1: Union[torch.Tensor, np.ndarray],
    activations2: Union[torch.Tensor, np.ndarray],
    layer_name: str,
) -> None:
    if isinstance(activations1, torch.Tensor):
        activations1 = activations1.detach().cpu().numpy()
    if isinstance(activations2, torch.Tensor):
        activations2 = activations2.detach().cpu().numpy()

    norm_axis = tuple(range(activations1.ndim - 1))
    print(norm_axis)
    activations1 = activations1.mean(axis=norm_axis)
    activations2 = activations2.mean(axis=norm_axis)

    x, y = (activations1, activations2)
    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, c=y, cmap="viridis", alpha=0.7, edgecolor="k", s=60)

    # Axis labels and title
    plt.xlabel(f"Input to {layer_name}", fontsize=14)
    plt.ylabel(f"Output of {layer_name}", fontsize=14)
    plt.title(f"Layer Input vs Output ({layer_name})", fontsize=16)

    plt.tight_layout()
    plt.show()


def histogram(
    data: Union[torch.Tensor, np.ndarray],
    viz_type: str,
    layer_name: str,
    bins: int = 30,
) -> None:
    if isinstance(data, torch.Tensor):
        data = data.detach().cpu().numpy()

    if viz_type.lower() in ["activation", "activations"]:
        norm_axis = tuple(range(data[0].ndim - 1))
        data = data[0].mean(axis=norm_axis)
    else:
        norm_axis = tuple(range(data.ndim - 1))
        data = data.mean(axis=norm_axis)

        if viz_type.lower() in ["gradient", "gradients"]:
            data = np.log(data)

    sns.histplot(
        data,
        bins=bins,
        kde=True,
        color="blue",
        edgecolor="black",
        label=layer_name,
    )
    plt.title(f"Distribution of Mean Activations for {layer_name}")
    plt.xlabel(f"Mean {viz_type} Value")
    plt.ylabel("Frequency")
    plt.legend()

    plt.tight_layout()
    plt.show()


def plot_cka(model1_activations: Dict, model2_activations: Dict) -> None:
    cka_matrices = np.zeros((len(model1_activations), len(model2_activations)))

    for i, v1 in enumerate(model1_activations.values()):
        for j, v2 in enumerate(model2_activations.values()):
            norm_axis_a1 = tuple(range(v1.ndim - 2))
            norm_axis_a2 = tuple(range(v2.ndim - 2))
            cka_value = cka(
                gram_linear(v1.numpy().mean(axis=norm_axis_a1)),
                gram_linear(v2.numpy().mean(axis=norm_axis_a2)),
            )
            cka_matrices[len(model1_activations) - i - 1, j] = cka_value

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cka_matrices,
        annot=False,
        fmt=".2f",
        xticklabels=list(model1_activations.keys()),
        yticklabels=list(model2_activations.keys())[::-1],
    )
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.title("CKA Matrix")
    plt.show()


def plot_query_attention_bar_seaborn(
    attn_scores: np.ndarray,
    query_index: int,
    tokens=None,
    title="Query Attention",
):
    attn_scores = np.array(attn_scores)
    seq_len = attn_scores.shape[0]

    query_attn = attn_scores[query_index]
    indices = list(range(seq_len))
    indices.remove(query_index)
    values = query_attn[indices]

    if tokens:
        labels = [tokens[i] for i in indices]
        query_token = tokens[query_index]
    else:
        labels = [f"Token {i}" for i in indices]
        query_token = f"Token {query_index}"

    sorted_pairs = sorted(zip(labels, values), key=lambda x: x[1], reverse=True)
    print(sorted_pairs)
    sorted_labels, sorted_values = zip(*sorted_pairs)

    # Plot
    df = pd.DataFrame({"Token": sorted_labels, "Attention Score": sorted_values})

    plt.figure(figsize=(8, 5))
    sns.barplot(x="Attention Score", y="Token", data=df, palette="Blues_r")
    plt.title(f"{title} (Query: {query_token})")
    plt.xlabel("Attention Score")
    plt.tight_layout()
    plt.show()

    return sorted_pairs


def plot_binary_attention_seaborn(
    attn_scores: np.ndarray,
    threshold: float,
    tokens: Optional[List] = None,
    title: str = "Binary Attention Map",
):
    attn_scores = np.array(attn_scores)
    binary_matrix = (attn_scores >= threshold).astype(int)

    if tokens is None:
        tokens = [f"Token {i}" for i in range(binary_matrix.shape[0])]

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        binary_matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=tokens,
        yticklabels=tokens,
        cbar=False,
        linewidths=0.5,
        linecolor="lightgrey",
    )
    plt.xticks(rotation=45)
    plt.title(f"{title} (threshold = {threshold})")
    plt.xlabel("Key")
    plt.ylabel("Query")
    plt.tight_layout()
    plt.show()
