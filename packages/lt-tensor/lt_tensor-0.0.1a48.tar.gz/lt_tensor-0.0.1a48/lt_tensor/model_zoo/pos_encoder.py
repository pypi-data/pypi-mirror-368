__all__ = [
    "RotaryEmbedding",
    "PositionalEncoding",
    "LearnedPositionalEncoding",
]

import math
import torch
from torch import nn, Tensor
from typing import Optional

class RotaryEmbedding(nn.Module):
    def __init__(self, dim: int, base: int = 10000):
        """
        Rotary Positional Embedding Module.
        Args:
            dim (int): The dimension of the rotary embedding (must be even).
            base (int): The base frequency scale (default: 10000).
        """
        super().__init__()
        assert dim % 2 == 0, "Rotary dimension must be even"
        self.dim = dim
        self.base = base

    def forward(self, x, seq_len=None):
        """
        Apply rotary embeddings to input tensor.
        Args:
            x (torch.Tensor): Input tensor of shape [batch, seq_len, dim].
            seq_len (int, optional): Override for sequence length.
        Returns:
            torch.Tensor: Tensor with rotary embeddings applied.
        """
        bsz, seq_len = x.shape[0], seq_len or x.shape[1]
        device = x.device

        pos = torch.arange(seq_len, dtype=torch.float32, device=device).unsqueeze(1)
        freqs = torch.pow(
            self.base, -torch.arange(0, self.dim, 2, device=device).float() / self.dim
        )
        angle = pos * freqs  # [seq_len, dim/2]

        sin = torch.sin(angle)
        cos = torch.cos(angle)

        # Expand and interleave to [seq_len, dim]
        sin = torch.stack((sin, sin), dim=-1).reshape(seq_len, self.dim)
        cos = torch.stack((cos, cos), dim=-1).reshape(seq_len, self.dim)

        sin = sin.unsqueeze(0).expand(bsz, -1, -1)  # [batch, seq_len, dim]
        cos = cos.unsqueeze(0).expand(bsz, -1, -1)

        return self.apply_rotary(x, sin, cos)

    def _apply_rotary(self, x, sin, cos):
        """This version may still be useful, but for now its the problem for the text model"""
        x1, x2 = x.chunk(2, dim=-1)
        return torch.cat((x1 * cos - x2 * sin, x2 * cos + x1 * sin), dim=-1)

    def apply_rotary(self, x, sin, cos):
        """x: [batch, seq_len, dim]  → assume dim is even"""
        b, s, d = x.shape
        x = x.view(b, s, d // 2, 2)  # [b, s, d//2, 2]
        sin = sin.view(b, s, d // 2, 2)
        cos = cos.view(b, s, d // 2, 2)

        # Apply rotation: even, odd = x[..., 0], x[..., 1]
        x_rotated = torch.stack(
            [
                x[..., 0] * cos[..., 0] - x[..., 1] * sin[..., 0],
                x[..., 0] * sin[..., 0] + x[..., 1] * cos[..., 0],
            ],
            dim=-1,
        )

        return x_rotated.view(b, s, d)  # Back to [b, s, d]


class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 8192):
        super().__init__()
        # create a matrix of [seq_len, hidden_dim] representing positional encoding for each token in sequence
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(
            1
        )  # (max_len, 1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2, dtype=torch.float)
            * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer("pe", pe, persistent=False)  # Shape: (1, max_len, d_model)

    def forward(self, x: Tensor, seq_len: Optional[Tensor] = None):
        # x shape: (batch_size, seq_len, d_model)
        s_sz = seq_len or x.size(1)
        x = x + self.pe[:, :s_sz]
        return x


class LearnedPositionalEncoding(nn.Module):
    def __init__(self, max_len: int, dim_model: int, dropout: float = 0.1):
        super().__init__()
        self.embedding = nn.Embedding(max_len, dim_model)
        self.dropout = nn.Dropout(dropout)
        self.max_len = max_len

    def forward(self, x: torch.Tensor, offset: int = 0) -> torch.Tensor:
        # x: [B, T, D] or [T, D]
        seq_len = x.size(1 if x.dim() == 3 else 0)
        if seq_len + offset > self.max_len:
            raise ValueError(
                f"Sequence length {seq_len + offset} exceeds max length {self.max_len}"
            )
        positions = torch.arange(offset, offset + seq_len, device=x.device)
        pos_embed = self.embedding(positions)
        if x.dim() == 3:
            pos_embed = pos_embed.unsqueeze(0).expand(x.size(0), -1, -1)  # [B, T, D]
        return self.dropout(x + pos_embed)
