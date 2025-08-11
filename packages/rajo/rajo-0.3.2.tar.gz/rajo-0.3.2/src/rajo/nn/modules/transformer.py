__all__ = [
    'Attention',
    'FeedForward',
    'MaxVitBlock',
    'MultiAxisAttention',
    'VitBlock',
]

from typing import Final, cast

import torch
import torch.nn.functional as F
from einops import rearrange
from einops.layers.torch import Rearrange
from packaging.version import Version
from torch import Tensor, nn

from .aggregates import pre_norm
from .context import ConvCtx
from .conv import mbconv
from .util import round8

_IS_TORCH_1_12 = Version('1.12') <= Version(torch.__version__) < Version('2.0')
_IS_TORCH_2X = Version(torch.__version__) >= Version('2.0')
_TORCH_MHA_AUTOCAST = True


class ReAttention(nn.Sequential):
    """Re-Attention from [DeepViT](https://arxiv.org/abs/2103.11886)"""

    def __init__(self, heads: int) -> None:
        super().__init__(
            Rearrange('b h i j -> b i j h'),
            nn.Linear(heads, heads, bias=False),
            nn.LayerNorm(heads),
            Rearrange('b i j h -> b h i j'),
        )
        nn.init.normal_(self[1].weight)


class Attention(nn.Module):
    """
    Multihead self-attention module (M-SA)
    from [ViT](https://openreview.net/pdf?id=YicbFdNTTy).

    Supports Re-attention mechanism
    from [DeepViT](https://arxiv.org/abs/2103.11886).
    """

    reattention: Final[bool]

    def __init__(
        self,
        dim: int,
        dim_head: int = 64,
        dropout: float = 0.0,
        qkv_bias: bool = False,
        reattention: bool = False,
    ) -> None:
        super().__init__()
        assert dim % dim_head == 0
        self.dim = dim
        self.heads = heads = dim // dim_head
        self.scale = dim_head**-0.5
        self.dropout = dropout

        self.to_qkv = nn.Sequential(
            fc := nn.Linear(dim, 3 * dim, bias=qkv_bias),
            Rearrange('b n (split h d) -> split b h n d', h=heads, split=3),
        )
        nn.init.normal_(fc.weight, 0, (2 / (dim + dim_head)) ** 0.5)

        self.attend = nn.Sequential(
            nn.Softmax(-1),
            nn.Dropout(dropout, inplace=True),
        )
        if reattention:
            self.attend.append(ReAttention(heads))

        self.to_out = nn.Sequential(
            Rearrange('b h n d -> b n (h d)'),
            fc := nn.Linear(dim, dim),
            nn.Dropout(dropout, inplace=True),
        )
        nn.init.xavier_normal_(fc.weight)

        self.dim = dim
        self.heads = heads
        self.qkv_bias = qkv_bias
        self.dropout = dropout
        self.reattention = reattention

    def __repr__(self) -> str:
        line = f'{self.dim}, heads={self.heads}'
        if self.qkv_bias:
            line += ', qkv_bias=True'
        if self.dropout:
            line += f', dropout={self.dropout}'
        if self.reattention:
            line += ', reattention=True'
        return f'{type(self).__module__}({line})'

    def forward(self, x: Tensor) -> Tensor:
        # Optimized eval-only impl since Torch 1.12
        if _IS_TORCH_1_12 and not self.training and not self.reattention:
            in_w, in_b, out_w, out_b = cast(
                'tuple[Tensor, ...]',
                (
                    self.to_qkv[0].weight,
                    self.to_qkv[0].bias,
                    self.to_out[1].weight,
                    self.to_out[1].bias,
                ),
            )
            tensor_args = (x, in_w, in_b, out_w, out_b)
            if (
                _TORCH_MHA_AUTOCAST or not torch.is_autocast_enabled()
            ) and not (
                torch.is_grad_enabled()
                and any([t.requires_grad for t in tensor_args])  # noqa: C419
            ):
                if torch.is_autocast_enabled():
                    # torch uses slowpath, but this allows it go fast
                    dtype = torch.get_autocast_gpu_dtype()
                    if in_b.dtype != dtype:
                        in_b = in_b.to(dtype)
                out, _ = torch._native_multi_head_attention(
                    x,
                    x,
                    x,
                    self.dim,
                    self.heads,
                    in_w,
                    in_b,
                    out_w,
                    out_b,
                    None,
                    False,
                )
                return out

        # b n dim -> b h n d
        qkv = self.to_qkv(x)
        q, k, v = qkv[0], qkv[1], qkv[2]  # make torchscript happy

        # Use FLASH-attention (https://arxiv.org/abs/2205.14135)
        # and Memory-Efficient attention from XFormers
        # for PyTorch 2.x
        if _IS_TORCH_2X and not self.reattention:
            dropout = self.dropout if self.is_train else 0
            out = F.scaled_dot_product_attention(q, k, v, dropout_p=dropout)

        else:
            # Compute weights for each token
            dots = torch.einsum('bhid,bhjd -> bhij', q, k)
            attn = self.attend(dots * self.scale)

            # Remix tokens using weights
            out = torch.einsum('bhij,bhjd -> bhid', attn, v)

        # Restore shape, b h n d -> b n (h d)
        return self.to_out(out)


class _RelativePositionalBias(nn.Module):
    def __init__(self, heads: int, window_size: int) -> None:
        super().__init__()

        wdiff = 2 * window_size - 1
        self.bias = nn.Sequential(
            nn.Embedding(wdiff**2, heads),
            Rearrange('i j h -> h i j'),
        )

        axis = torch.arange(window_size)
        grid = torch.stack(torch.meshgrid(axis, axis, indexing='ij'), -1)
        pos = rearrange(grid, 'i j c -> (i j) 1 c') - rearrange(
            grid, 'i j c -> 1 (i j) c'
        )
        pos -= pos.min()
        indices = pos @ torch.tensor([wdiff, 1])
        self.register_buffer('indices', indices, persistent=False)

    def forward(self) -> Tensor:
        return self.bias(self.indices)


class MultiAxisAttention(nn.Module):
    """
    Multi-axis self-attention (Max-SA)
    from [MaxViT](https://arxiv.org/abs/2204.01697)
    """

    def __init__(
        self,
        dim: int,
        dim_head: int = 32,
        dropout: float = 0.0,
        qkv_bias: bool = False,
        window_size: int = 7,
    ) -> None:
        super().__init__()
        assert dim % dim_head == 0
        heads = dim // dim_head

        self.scale = dim_head**-0.5
        self.to_qkv = nn.Sequential(
            nn.Linear(dim, dim * 3, bias=qkv_bias),
            Rearrange('... i (s h d) -> s ... h i d', s=3, h=heads),
        )
        self.bias = _RelativePositionalBias(heads, window_size)

        self.attend = nn.Sequential(
            nn.Softmax(-1),
            nn.Dropout(dropout, inplace=True),
        )
        self.to_out = nn.Sequential(
            Rearrange('... h i d -> ... i (h d)'),
            nn.Linear(dim, dim, bias=False),
            nn.Dropout(dropout, inplace=True),
        )
        self.dim = dim
        self.heads = heads
        self.window_size = window_size
        self.qkv_bias = qkv_bias
        self.dropout = dropout

    def __repr__(self) -> str:
        line = f'{self.dim}'
        line += f', heads={self.heads}, window_size={self.window_size}'
        if self.qkv_bias:
            line += ', qkv_bias=True'
        if self.dropout:
            line += f', dropout={self.dropout}'
        return f'{type(self).__name__}({line})'

    def forward(self, x: Tensor) -> Tensor:
        # ... i d -> ... i d, self-attention over i
        q, k, v = self.to_qkv(x).unbind(0)  # ... h i d

        sim = torch.einsum('... i d, ... j d -> ... i j', q, k) * self.scale
        sim += self.bias()
        attn = self.attend(sim)

        # aggregate
        out = torch.einsum('... i j, ... j d -> ... i d', attn, v)

        # combine heads out
        return self.to_out(out)


class FeedForward(nn.Sequential):
    def __init__(self, dim: int, ratio: float, dropout: float = 0.0) -> None:
        dim_inner = round8(dim * ratio)
        super().__init__(
            nn.Linear(dim, dim_inner),
            nn.GELU(),
            nn.Dropout(dropout, inplace=True),
            nn.Linear(dim_inner, dim),
            nn.Dropout(dropout, inplace=True),
        )
        self.dim = dim
        self.dim_inner = dim_inner
        self.dropout = dropout

    def __repr__(self) -> str:
        line = f'{self.dim}, dim_inner={self.dim_inner}'
        if self.dropout:
            line += f', dropout={self.dropout}'
        return f'{type(self).__name__}({line})'


# ----------------------------- complete blocks ------------------------------


class VitBlock(nn.Sequential):
    def __init__(
        self,
        dim: int,
        dim_head: int,
        mlp_ratio: float = 4.0,
        dropout: float = 0.0,
        qkv_bias: bool = False,
        reattn: bool = False,
    ) -> None:
        super().__init__(
            pre_norm(Attention(dim, dim_head, dropout, qkv_bias, reattn)),
            pre_norm(FeedForward(dim, mlp_ratio, dropout)),
        )


class MaxVitBlock(nn.Sequential):
    def __init__(
        self,
        dim: int,
        dim_head: int,
        window: int,
        stride: int = 1,
        bn_ratio: float = 4.0,
        se_ratio: float = 0.25,
        mlp_ratio: float = 4,
        dropout: float = 0.0,
        qkv_bias: bool = False,
        ctx: ConvCtx | None = None,
    ) -> None:
        super().__init__(
            # mbconv
            mbconv(dim, stride, bn_ratio, se_ratio, dropout, ctx),
            # block attention
            Rearrange('b d (x u) (y v) -> b x y (u v) d', u=window, v=window),
            pre_norm(
                MultiAxisAttention(dim, dim_head, dropout, qkv_bias, window)
            ),
            pre_norm(FeedForward(dim, mlp_ratio, dropout)),
            Rearrange('b x y (u v) d -> b d (x u) (y v)', u=window, v=window),
            # grid attention
            Rearrange('b d (u x) (v y) -> b x y (u v) d', u=window, v=window),
            pre_norm(
                MultiAxisAttention(dim, dim_head, dropout, qkv_bias, window)
            ),
            pre_norm(FeedForward(dim, mlp_ratio, dropout)),
            Rearrange('b x y (u v) d -> b d (u x) (v y)', u=window, v=window),
        )
