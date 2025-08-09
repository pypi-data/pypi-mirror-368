from typing import Tuple

import torch
from torch import nn
from torch.nn import functional as F


class FFN(nn.Module):
    def __init__(self, n_feats: int, n_classes: int) -> None:
        super().__init__()
        self.ffn = nn.Sequential(
            nn.LayerNorm(n_feats),
            nn.Dropout(0.1),
            nn.Linear(n_feats, 512),
            nn.ReLU(),
            nn.LayerNorm(512),
            nn.Dropout(0.1),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.LayerNorm(512),
            nn.Dropout(0.1),
            nn.Linear(512, n_classes),
            nn.Softmax(dim=-1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.ffn(x)


class FFNKai(nn.Module):
    def __init__(self, n_feats: int, n_classes: int) -> None:
        super().__init__()
        self.ffn = nn.Sequential(
            nn.LayerNorm(n_feats),
            nn.Dropout(0.1),
            nn.Linear(n_feats, 512),
            nn.LayerNorm(512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, 512),
            nn.LayerNorm(512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, n_classes),
            nn.Softmax(dim=-1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.ffn(x)


class FFNSiLU(nn.Module):
    def __init__(self, n_feats: int, n_classes: int) -> None:
        super().__init__()
        self.ffn = nn.Sequential(
            nn.LayerNorm(n_feats),
            nn.Dropout(0.1),
            nn.Linear(n_feats, 512),
            nn.SiLU(),
            nn.LayerNorm(512),
            nn.Dropout(0.1),
            nn.Linear(512, 512),
            nn.SiLU(),
            nn.LayerNorm(512),
            nn.Dropout(0.1),
            nn.Linear(512, n_classes),
            nn.Softmax(dim=-1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.ffn(x)


class FFNLReLU(nn.Module):
    def __init__(self, n_feats: int, n_classes: int) -> None:
        super().__init__()
        self.ffn = nn.Sequential(
            nn.LayerNorm(n_feats),
            nn.Dropout(0.1),
            nn.Linear(n_feats, 512),
            nn.LeakyReLU(0.1),
            nn.LayerNorm(512),
            nn.Dropout(0.1),
            nn.Linear(512, 512),
            nn.LeakyReLU(0.1),
            nn.LayerNorm(512),
            nn.Dropout(0.1),
            nn.Linear(512, n_classes),
            nn.Softmax(dim=-1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.ffn(x)


class FFN2(nn.Module):
    def __init__(self, n_feats: int, n_classes: int) -> None:
        super().__init__()
        self.ffn = nn.Sequential(
            nn.BatchNorm1d(n_feats),
            nn.Dropout(0),
            nn.Linear(n_feats, 512),
            nn.LeakyReLU(),
            nn.BatchNorm1d(512),
            nn.Dropout(0.1),
            nn.Linear(512, 512),
            nn.LeakyReLU(),
            nn.BatchNorm1d(512),
            nn.Dropout(0.1),
            nn.Linear(512, n_classes),
            nn.Softmax(dim=-1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.ffn(x)


class FFNResidual(nn.Module):
    def __init__(self, n_feats: int, n_classes: int) -> None:
        super().__init__()
        self.ffn = nn.Sequential(
            nn.LayerNorm(n_feats),
            nn.Dropout(0.1),
            nn.Linear(n_feats, 512),
            nn.ReLU(),
            nn.LayerNorm(512),
            nn.Dropout(0.1),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.LayerNorm(512),
            nn.Dropout(0.1),
            nn.Linear(512, n_classes),
        )
        self.residual = nn.Linear(n_feats, n_classes)
        self.softmax = nn.Softmax(dim=-1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.softmax(self.ffn(x) + self.residual(x))


class OverfitFFN(nn.Module):
    def __init__(self, n_feats: int, n_classes: int) -> None:
        super().__init__()
        self.ffn = nn.Sequential(
            nn.Linear(n_feats, 512),
            nn.ReLU(),
            nn.Linear(512, 1024),
            nn.ReLU(),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, n_classes),
            nn.Softmax(dim=-1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.ffn(x)


class AttentionScore(nn.Module):
    def __init__(self, head_dim: int) -> None:
        super().__init__()
        self.head_dim = head_dim

    def forward(self, q, k) -> torch.Tensor:
        return F.softmax((q @ k.transpose(-2, -1)) / (self.head_dim**0.5), dim=-1)


class AttentionBlock(nn.Module):
    def __init__(self, dim: int, heads: int) -> None:
        super().__init__()
        self.heads = heads
        self.dim = dim
        self.head_dim = dim // heads

        self.norm = nn.LayerNorm(dim)
        self.attn = AttentionScore(self.head_dim)
        self.q_proj = nn.Linear(dim, dim, bias=False)
        self.k_proj = nn.Linear(dim, dim, bias=False)
        self.v_proj = nn.Linear(dim, dim, bias=False)
        self.out_proj = nn.Linear(dim, dim)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # x: (B, T, D)
        B, T, D = x.shape

        x = self.norm(x)

        # Project Q, K, V
        q = self.q_proj(x).view(B, T, self.heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(B, T, self.heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(B, T, self.heads, self.head_dim).transpose(1, 2)

        # Compute scaled dot-product attention
        attn = self.attn(q, k)

        # Attention output
        out = attn @ v  # (B, heads, T, head_dim)
        out = out.transpose(1, 2).contiguous().view(B, T, D)  # (B, T, D)
        out = self.out_proj(out)

        return out, attn


class TinyTabularAttentionModel(nn.Module):
    def __init__(
        self,
        input_dim: int = 10,
        seq_len: int = 4,
        dim: int = 32,
        heads: int = 1,
        num_classes: int = 2,
    ):
        super().__init__()
        self.seq_len = seq_len
        self.token_dim = dim

        self.input_proj = nn.Linear(input_dim, seq_len * dim)
        self.attn_block = AttentionBlock(dim, heads)

        self.classifier = nn.Sequential(
            nn.Linear(dim, dim), nn.ReLU(), nn.Linear(dim, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, F)
        B = x.size(0)
        x = self.input_proj(x).view(B, self.seq_len, self.token_dim)  # [B, T, D]
        out, self.attn = self.attn_block(x)  # out: (B, T, D), attn: (B, heads, T, T)
        pooled = out.mean(dim=1)  # (B, D)
        logits = self.classifier(pooled)

        return logits
