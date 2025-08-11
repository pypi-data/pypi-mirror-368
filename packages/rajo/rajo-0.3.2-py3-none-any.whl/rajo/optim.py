__all__ = ['AdamW', 'Lamb', 'Lion', 'RAdam', 'SGDW']

from collections import defaultdict
from weakref import ref
from collections.abc import Callable, Iterable, Sequence
from dataclasses import InitVar, asdict, dataclass, field, fields
from math import sqrt
from typing import Any, NamedTuple, cast, final, overload

import torch
from torch import Tensor
from torch.nn.parameter import Parameter
from torch.optim.optimizer import Optimizer

from . import _foreach

_sentinel = object()


class _GradState(NamedTuple):
    p: list[Parameter]
    grad: list[Tensor]
    bufs: list[list[Tensor]]


@dataclass
class SingleGroupOptimizer(Optimizer):
    params: InitVar[list[Parameter]]
    states: dict[Parameter, list[Tensor]] = field(init=False, repr=False)
    extras: dict[str, Any] = field(default_factory=dict)
    _step = 0

    def __post_init__(self, params: list[Parameter]) -> None:
        self.states = {p: [] for p in params}

        # torch.optim.lr_scheduler compat
        proxy = cast('dict[str, Any]', _DictLikeProxy(ref(self)))
        self.param_groups = [proxy]

    # torch.optim.lr_scheduler compat

    @property
    def defaults(self) -> dict:
        return {
            k: v
            for k, v in asdict(self).items()
            if k not in SingleGroupOptimizer.__dataclass_fields__
        }

    @defaults.setter
    def defaults(self, value) -> None:
        raise RuntimeError

    # core API

    @final
    def zero_grad(self, set_to_none: bool = True) -> None:
        if set_to_none:
            for p in self.states:
                p.grad = None
        else:
            for _, grads, _ in self._state_groups():
                _foreach.zero_(grads)

    def common_step_args(self) -> dict:
        return {}

    def __getstate__(self):
        raise NotImplementedError

    @final
    def state_dict(self) -> dict[str, Any]:
        return asdict(self) | {
            '_step': self._step,
            'grads': [p.grad for p in self.states],
            'states': [*self.states.values()],
        }

    @final
    @torch.no_grad()
    def load_state_dict(self, state: dict) -> None:
        self.__dict__.update(
            {k: v for k, v in state.items() if k not in ('grads', 'states')}
        )
        for p, g in zip(self.states, state['grads']):
            if g is None:
                p.grad = None
            elif p.grad is None:
                p.grad = g.clone().detach_().to(p.device, non_blocking=True)
            else:
                p.grad.copy_(g.to(p.device, non_blocking=True, copy=False))

        for dst, src in zip(self.states.values(), state['states']):
            dst[:] = src

    def _state_groups(self) -> Iterable[_GradState]:
        r: dict[tuple, _GradState] = defaultdict(
            lambda: _GradState([], [], [])
        )
        for p, ts in self.states.items():
            if p.grad is None:
                continue
            num_values = sum(t is not None for t in ts)
            s = r[p.device, p.dtype, p.grad.is_sparse, num_values]
            s.p.append(p)
            s.grad.append(p.grad)
            s.bufs.append(ts)

        return r.values()

    @overload
    def step(self, closure: None = ...) -> None: ...

    @overload
    def step(self, closure: Callable[[], float]) -> float: ...

    @final
    @torch.no_grad()
    def step(self, closure: Callable[[], float] | None = None) -> float | None:
        self._step += 1
        with torch.enable_grad():
            loss = closure() if closure else None

        kwargs = self.common_step_args()
        for params, grads, bufs in self._state_groups():
            with torch.no_grad():
                self.device_step(params, grads, bufs, **kwargs)

        return loss

    @final
    def zero_init(
        self,
        params: Sequence[Parameter],
        bufs: Sequence[list[Tensor]],
        num_bufs: int,
    ) -> Sequence[Sequence[Tensor]]:
        for p, bufs_ in zip(params, bufs):
            if not bufs_:
                bufs_.extend(torch.zeros_like(p) for _ in range(num_bufs))
        return [*zip(*bufs)]

    def device_step(
        self,
        params: Sequence[Parameter],
        grads: Sequence[Tensor],
        bufs: Sequence[list[Tensor]],
        **kwargs,
    ):
        raise NotImplementedError


@dataclass
class SGDW(SingleGroupOptimizer):
    """Implements stochastic gradient descent (optionally with momentum).

    Nesterov momentum is based on the formula from
    `On the importance of initialization and momentum in deep learning`__.

    __ http://www.cs.toronto.edu/%7Ehinton/absps/momentum.pdf

    Fixes weight decay rule of `torch.optim.SGD`
    """

    lr: float = 0.003
    momentum: float = 0
    dampening: float = 0
    weight_decay: float = 0
    nesterov: bool = False

    def __post_init__(self, params) -> None:
        assert self.lr >= 0
        assert self.momentum >= 0
        assert self.weight_decay >= 0
        assert not self.nesterov or (
            self.momentum > 0 and self.dampening == 0
        ), 'Nesterov momentum requires a momentum and zero dampening'
        super().__post_init__(params)

    def device_step(
        self,
        params: Sequence[Parameter],
        grads: Sequence[Tensor],
        bufs: Sequence[list[Tensor]],
        **kwargs,
    ) -> None:
        if self.weight_decay != 0:
            _foreach.mul_(params, 1 - self.lr * self.weight_decay)

        if self.momentum != 0:
            if bufs[0]:
                avg = [bufs_[0] for bufs_ in bufs]
                _foreach.mul_(avg, self.momentum)
                _foreach.add_(avg, grads, alpha=1 - self.dampening)
            else:
                for grad, bufs_ in zip(grads, bufs):
                    bufs_.append(grad.clone().detach_())
                avg = [bufs_[0] for bufs_ in bufs]

            if self.nesterov:
                _foreach.add_(grads, avg, alpha=self.momentum)
            else:
                grads = avg

        _foreach.add_(params, grads, alpha=-self.lr)


@dataclass
class AdamW(SingleGroupOptimizer):
    r"""Implements AdamW algorithm.

    .. _Adam\: A Method for Stochastic Optimization:
        https://arxiv.org/abs/1412.6980
    .. _Decoupled Weight Decay Regularization:
        https://arxiv.org/abs/1711.05101
    .. _On the Convergence of Adam and Beyond:
        https://openreview.net/forum?id=ryQu7f-RZ

    Similar to `torch.optim.AdamW`
    """

    lr: float = 1e-3
    betas: tuple[float, float] = (0.9, 0.999)
    eps: float = 1e-8
    weight_decay: float = 1e-2
    amsgrad: bool = False

    def __post_init__(self, params) -> None:
        assert self.lr >= 0.0
        assert self.eps >= 0.0
        for i, beta in enumerate(self.betas):
            assert (
                0.0 <= beta < 1.0
            ), f'Invalid beta at index {i}: {self.betas}'
        super().__post_init__(params)

    def common_step_args(self) -> dict:
        beta1, beta2 = self.betas
        bias_correction1 = 1 - beta1**self._step
        bias_correction2 = 1 - beta2**self._step
        step_size = self.lr * sqrt(bias_correction2) / bias_correction1
        return {'step_size': step_size}

    def device_step(
        self,
        params: Sequence[Parameter],
        grads: Sequence[Tensor],
        bufs: Sequence[list[Tensor]],
        *,
        step_size=1,
        **kwargs,
    ) -> None:
        if self.amsgrad:
            avg, avg_sq, max_avg_sq = self.zero_init(params, bufs, 3)
        else:
            avg, avg_sq = self.zero_init(params, bufs, 2)
            max_avg_sq = []

        beta1, beta2 = self.betas

        _foreach.lerp_(avg, grads, weight=1 - beta1)

        _foreach.mul_(avg_sq, beta2)
        _foreach.addcmul_(avg_sq, grads, grads, value=1 - beta2)

        if self.weight_decay != 0:
            _foreach.mul_(params, 1 - self.lr * self.weight_decay)

        if self.amsgrad:
            _foreach.maximum_(max_avg_sq, avg_sq)
            avg_sq = max_avg_sq

        denom = _foreach.sqrt(avg_sq)
        _foreach.add_(denom, self.eps)
        _foreach.addcdiv_(params, avg, denom, value=-step_size)


@dataclass
class RAdam(SingleGroupOptimizer):
    r"""Implements RAdam algorithm.

    .. _On the variance of the adaptive learning rate and beyond:
        https://arxiv.org/abs/1908.03265
    .. _author's implementation:
        https://github.com/LiyuanLucasLiu/RAdam

    Fixes weight decay rule of `torch.optim.RAdam`
    """

    lr: float = 1e-3
    betas: tuple[float, float] = (0.9, 0.999)
    weight_decay: float = 0
    radam: bool = True  # If false, equals to plain AdamW
    decay_to_sgd: bool = True
    eps: float = 1e-8

    def common_step_args(self) -> dict:
        beta1, beta2 = self.betas
        n_sma_max = 2 / (1 - beta2) - 1

        bias_correction1 = 1 - beta1**self._step
        step_size = self.lr / bias_correction1

        bias_correction2 = 1 - beta2**self._step
        if not self.radam:
            return {'step_size': step_size * sqrt(bias_correction2)}

        beta2_t = beta2**self._step
        n_sma = n_sma_max - 2 * self._step * beta2_t / bias_correction2

        # more conservative since it's an approximated value
        # variance is not tractable
        if n_sma < 5:
            return {'is_tractable': False, 'step_size': step_size}

        k = (n_sma - 4) * (n_sma - 2) / n_sma
        k_max = (n_sma_max - 4) * (n_sma_max - 2) / n_sma_max
        return {'step_size': step_size * sqrt(bias_correction2 * k / k_max)}

    def device_step(
        self,
        params: Sequence[Parameter],
        grads: Sequence[Tensor],
        bufs: Sequence[list[Tensor]],
        *,
        is_tractable=True,
        step_size=1,
        **kwargs,
    ) -> None:
        avg, avg_sq = self.zero_init(params, bufs, 2)
        beta1, beta2 = self.betas

        _foreach.lerp_(avg, grads, weight=1 - beta1)

        _foreach.mul_(avg_sq, beta2)
        _foreach.addcmul_(avg_sq, grads, grads, value=1 - beta2)

        if self.weight_decay != 0:
            _foreach.mul_(params, 1 - self.weight_decay * self.lr)

        if is_tractable:
            denom = _foreach.sqrt(avg_sq)
            _foreach.add_(denom, self.eps)
            _foreach.addcdiv_(params, avg, denom, value=-step_size)

        elif self.decay_to_sgd:
            _foreach.add_(params, avg, alpha=-step_size)


@dataclass
class Lion(SingleGroupOptimizer):
    r"""Implements Lion algorithm.

    .. _Symbolic Discovery of Optimization Algorithms:
        https://arxiv.org/abs/2302.06675
    .. _reference implementation:
        https://github.com/google/automl/tree/master/lion
    """

    lr: float = 1e-4
    betas: tuple[float, float] = (0.9, 0.99)
    weight_decay: float = 0.0

    def device_step(
        self,
        params: Sequence[Parameter],
        grads: Sequence[Tensor],
        bufs: Sequence[list[Tensor]],
        **kwargs,
    ) -> None:
        (avg,) = self.zero_init(params, bufs, 1)
        beta1, beta2 = self.betas

        if self.weight_decay != 0:
            _foreach.mul_(params, 1 - self.lr * self.weight_decay)

        update = _foreach.lerp(avg, grads, weight=1 - beta1)
        for u in update:
            u.sign_()
        _foreach.add_(params, update, alpha=-self.lr)

        _foreach.lerp_(avg, grads, weight=1 - beta2)


@dataclass
class Lamb(SingleGroupOptimizer):
    r"""Implements Lamb algorithm.
    It has been proposed in `Large Batch Optimization for Deep Learning:
    Training BERT in 76 minutes`__.
    Arguments:
        params: iterable of parameters to optimize or dicts defining
            parameter groups
        lr: learning rate (default: 1e-3)
        betas: coefficients used for computing
            running averages of gradient and its square (default: (0.9, 0.999))
        eps: term added to the denominator to improve
            numerical stability (default: 1e-8)
        weight_decay: weight decay (L2 penalty) (default: 0)
        clamp_value: clamp weight_norm in (0,clamp_value) (default: 10)
            set to a high value to avoid it (e.g 10e3)
        adam: always use trust ratio = 1, which turns this
            into Adam. Useful for comparison purposes. (default: False)
        debias: debias adam by (1 - beta**step) (default: False)

    __ https://arxiv.org/abs/1904.00962
    Note:
        Reference code: https://github.com/cybertronai/pytorch-lamb
    """

    lr: float = 1e-3
    betas: tuple[float, float] = (0.9, 0.999)
    weight_decay: float = 0.0
    eps: float = 1e-8
    clamp_value: float = 10
    adam: bool = False
    debias: bool = False

    def common_step_args(self) -> dict:
        if self.debias:
            return {'step_size': self.lr}

        beta1_t, beta2_t = (beta**self._step for beta in self.betas)
        correction1 = 1 - beta1_t
        correction2 = 1 - beta2_t
        return {'step_size': self.lr * (correction2**0.5) / correction1}

    def device_step(
        self,
        params: Sequence[Parameter],
        grads: Sequence[Tensor],
        bufs: Sequence[list[Tensor]],
        *,
        step_size: float = 1,
        **kwargs,
    ) -> None:
        avg, avg_sq = self.zero_init(params, bufs, 2)
        beta1, beta2 = self.betas

        _foreach.lerp_(avg, grads, weight=1 - beta1)

        _foreach.mul_(avg_sq, beta2)
        _foreach.addcmul_(avg_sq, grads, grads, value=1 - beta2)

        # update = avg / (sqrt(avg_sq) + eps)
        denom = _foreach.sqrt(avg_sq)
        _foreach.add_(denom, self.eps)
        update = _foreach.div(avg, denom)

        if self.weight_decay:
            _foreach.add_(update, params, alpha=self.weight_decay)

        if not self.adam:
            update_norm = torch.stack(_foreach.norm(update))
            params_norm = torch.stack(_foreach.norm(params))
            _foreach.clamp_max_(params_norm, self.clamp_value)

            trust_ratio = torch.where(
                (update_norm * params_norm).bool(),
                params_norm / update_norm,
                torch.as_tensor(1, device=update_norm.device),
            )
            _foreach.mul_(update, trust_ratio.unbind())

        _foreach.add_(params, update, alpha=-step_size)


# ------------------- torch.optim.lr_scheduler compat ------------------------


@dataclass(frozen=True, slots=True)
class _DictLikeProxy:
    sgo: ref[SingleGroupOptimizer]

    def _get_state(
        self,
    ) -> tuple[SingleGroupOptimizer, dict[str, Any]]:
        obj = self.sgo()
        assert obj
        return obj, obj.__dict__

    def keys(self) -> list[str]:
        g, items = self._get_state()
        return sorted({'params', *items, *g.extras} - _forbidden_keys)

    def setdefault(self, key: str, default):
        g, items = self._get_state()
        assert key not in _forbidden_keys
        if (v := items.get(key, _sentinel)) is not _sentinel:
            return v
        return g.extras.setdefault(key, default)

    def __getitem__(self, key: str):
        g, items = self._get_state()
        if key == 'params':  # expose
            return list(g.states)
        assert key not in _forbidden_keys
        if (v := items.get(key, _sentinel)) is not _sentinel:
            return v
        return g.extras[key]

    def __setitem__(self, key: str, value) -> None:
        g, items = self._get_state()
        assert key not in _forbidden_keys
        if key in items:
            items[key] = value
        else:
            g.extras[key] = value


_forbidden_keys = {f.name for f in fields(SingleGroupOptimizer)}
