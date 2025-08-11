__all__ = ['materialize']

import torch
from torch import nn
from torch.nn.modules import lazy

from .nn.modules.lazy import _materialize_cls
from .util import eval_


def materialize(model: nn.Module, *args, **kwargs) -> None:
    """
    Materialize all the lazy modules within model.
    Safely call forward() if args or kwargs are passed.
    """
    modules = {
        name: m
        for name, m in model.named_modules()
        if isinstance(m, lazy.LazyModuleMixin)
    }
    if not modules:
        return

    uninitialized = {
        name: m
        for name, m in modules.items()
        if m.has_uninitialized_params()  # type: ignore[misc]
    }
    if not uninitialized:  # Complete initialization without forward() call
        for m in modules.values():
            _materialize_cls(m)  # type: ignore[arg-type]
        return

    if args or kwargs:  # Initialize from forward() call
        with eval_(model), torch.no_grad():
            model(*args, **kwargs)
        return

    raise RuntimeError(
        'Found uninitialized lazy modules but no example inputs were passed '
        'to initialize them:\n'
        f'{[*uninitialized]}'
    )
