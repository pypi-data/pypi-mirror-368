__all__ = [
    'Cat',
    'Encoder',
    'Ensemble',
    'Gate',
    'Residual',
    'ResidualCat',
    'pre_norm',
]

from collections.abc import Iterable
from typing import Final, Literal

import torch
from torch import Tensor, jit, nn
from torch.utils.checkpoint import checkpoint

from .lazy import LazyLayerNorm
from .util import LazyNormFn

type _EnsembleMode = Literal['cat', 'sum', 'mean']


class Ensemble(nn.ModuleList):
    mode: Final[_EnsembleMode]

    def __init__(
        self, *branches: nn.Module | Iterable[nn.Module], mode: _EnsembleMode
    ) -> None:
        modules = (
            b if isinstance(b, nn.Module) else nn.Sequential(*b)
            for b in branches
        )
        super().__init__(modules)
        self.mode = mode

    def _cat(self, xs: list[Tensor]) -> Tensor:
        return torch.cat(xs, dim=1)

    def _sum(self, xs: list[Tensor]) -> Tensor:
        r = xs[0]
        for x in xs[1:]:
            r += x
        return r

    def _mean(self, xs: list[Tensor]) -> Tensor:
        r = xs[0]
        for n, x in enumerate(xs[1:], 2):
            r.lerp_(x, r.new_tensor(1 / n))
        return r

    def forward(self, x: Tensor) -> Tensor:
        ys: list[Tensor] = [m(x) for m in self]
        if self.mode == 'cat':
            return self._cat(ys)

        if self.mode == 'sum':
            return self._sum(ys)

        if self.mode == 'mean':
            return self._mean(ys)

        raise NotImplementedError


class _Sequential(nn.ModuleList):
    """
    This exists since TorchScript doesn't support inheritance, so the
    superclass method (_core_forward) needs to have a name other than `forward`
    that can be accessed in a subclass.
    See https://github.com/pytorch/pytorch/issues/42885.
    """

    def __init__(self, *modules: nn.Module) -> None:
        super().__init__(modules)

    def seq(self, x: Tensor) -> Tensor:
        # Replicates nn.Sequential.forward
        for m in self:
            x = m(x)
        return x


class ResidualCat(_Sequential):
    """Returns `cat([input, self(input)], dim=1)`, useful for U-Net"""

    def forward(self, x: Tensor) -> Tensor:
        return torch.cat([x, self.seq(x)], 1)


class Gate(_Sequential):
    """Returns input * self(input)"""

    def forward(self, x: Tensor) -> Tensor:
        return x * self.seq(x)


class Residual(_Sequential):
    """Returns input + self(input)"""

    def forward(self, x: Tensor) -> Tensor:
        return x + self.seq(x)


class Cat(_Sequential):
    """Computes the following:
    ```
    x = torch.cat(xs, 1)
    for m in modules:
        x = m(x)
    return x
    ```
    Checkpoints if makes sense.
    """

    def cat(self, xs: list[Tensor]) -> Tensor:
        x = xs[0] if len(xs) == 1 else torch.cat(xs, 1)
        return self.seq(x)

    @jit.ignore()
    def _cp_proxy(self, xs: list[Tensor]) -> Tensor:
        def closure(*xs: Tensor) -> Tensor:
            return self.cat([*xs])

        return checkpoint(closure, *xs)

    def forward(self, xs: list[Tensor]) -> Tensor:
        if jit.is_scripting() or jit.is_tracing():
            # checkpoint fails with JIT
            return self.cat(xs)

        if len(self) and any([x.requires_grad for x in xs]):  # noqa: C419
            return self._cp_proxy(xs)

        return self.cat(xs)


def pre_norm(*fn: nn.Module, norm: LazyNormFn = LazyLayerNorm) -> Residual:
    """Returns input + fn(norm(input))"""
    return Residual(norm(), *fn)


class Encoder(nn.Sequential):
    def __init__(
        self,
        stem: nn.Module,
        levels: nn.Module,
        head: nn.Module,
    ) -> None:
        super().__init__()
        self.stem = stem
        self.levels = levels
        self.head = head
