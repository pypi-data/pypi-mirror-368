__all__ = [
    'LazyBias2d',
    'LazyBlurPool2d',
    'LazyConv2dWs',
    'LazyGroupNorm',
    'LazyLayerNorm',
]

from torch import Size, Tensor, nn
from torch.nn.modules import lazy
from torch.nn.parameter import UninitializedBuffer, UninitializedParameter

from .primitive import Bias2d, BlurPool2d, Conv2dWs


def _materialize_cls(m: lazy._LazyProtocol) -> None:
    """
    Fixes incomplete implementation of LazyModuleMixin._lazy_load_hook

    Does the same as LazyModuleMixin._infer_parameters does,
    except no input is needed.

    By default, if all module's parameters are loaded during load_state_dict,
    _lazy_load_hook doen't mutate class.
    Because of that even completely initialized modules are left as lazy,
    and require calling forward() to trigger class mutation.

    This function cancels this requirement.
    """
    # FIXME: When merged to an upstream, do nothing
    assert isinstance(m, lazy.LazyModuleMixin)

    m._initialize_hook.remove()
    m._load_hook.remove()
    delattr(m, '_initialize_hook')
    delattr(m, '_load_hook')
    if m.cls_to_become is not None:
        m.__class__ = m.cls_to_become


class _LazyModuleMixinV2(lazy.LazyModuleMixin):
    def _lazy_load_hook(self: lazy._LazyProtocol, *args, **kwargs) -> None:
        super()._lazy_load_hook(*args, **kwargs)  # type: ignore[safe-super]

        if not self.has_uninitialized_params():  # type: ignore[attr-defined]
            _materialize_cls(self)


class _LazyBase(_LazyModuleMixinV2):
    def reset_parameters(self) -> None:
        if not self.has_uninitialized_params():  # type: ignore[misc]
            # Mypy doesnt like this super call in a mixin
            super().reset_parameters()  # type: ignore[misc]

    def initialize_parameters(self, x: Tensor) -> None:
        if self.has_uninitialized_params():  # type: ignore[misc]
            self.materialize(x.shape)
            self.reset_parameters()

    def materialize(self, shape: Size) -> None:
        raise NotImplementedError


class LazyLayerNorm(_LazyBase, nn.LayerNorm):
    cls_to_become = nn.LayerNorm

    weight: UninitializedParameter  # type: ignore[assignment]
    bias: UninitializedParameter  # type: ignore[assignment]
    normalized_shape: tuple[int, ...]

    def __init__(
        self, rank: int = 1, eps: float = 1e-5, elementwise_affine: bool = True
    ) -> None:
        super().__init__([0] * rank, eps, False)
        self.elementwise_affine = elementwise_affine
        if self.elementwise_affine:
            self.weight = UninitializedParameter()
            self.bias = UninitializedParameter()

    def materialize(self, shape: Size) -> None:
        rank = len(self.normalized_shape)
        self.normalized_shape = tuple(shape[-rank:])
        if self.elementwise_affine:
            self.weight.materialize(self.normalized_shape)
            self.bias.materialize(self.normalized_shape)


class LazyGroupNorm(_LazyBase, nn.GroupNorm):
    cls_to_become = nn.GroupNorm

    weight: UninitializedParameter  # type: ignore[assignment]
    bias: UninitializedParameter  # type: ignore[assignment]

    def __init__(
        self, num_groups: int, eps: float = 1e-5, affine: bool = True
    ) -> None:
        super().__init__(num_groups, 0, eps, False)
        self.affine = affine
        if self.affine:
            self.weight = UninitializedParameter()
            self.bias = UninitializedParameter()

    def materialize(self, shape: Size) -> None:
        self.num_channels = shape[1]
        if self.affine:
            self.weight.materialize((self.num_channels,))
            self.bias.materialize((self.num_channels,))


class LazyConv2dWs(nn.LazyConv2d):
    cls_to_become = Conv2dWs


class LazyBlurPool2d(_LazyBase, BlurPool2d):
    cls_to_become = BlurPool2d

    weight: UninitializedBuffer

    def __init__(
        self,
        kernel: int = 4,
        stride: int = 2,
        padding: int = 1,
        padding_mode: str = 'reflect',
    ) -> None:
        super().__init__(0, kernel, stride, padding, padding_mode)
        self.weight = UninitializedBuffer()

    def materialize(self, shape: Size) -> None:
        self.in_channels = self.out_channels = shape[-3]
        self.weight.materialize((self.out_channels, 1, *self.kernel_size))


class LazyBias2d(_LazyBase, Bias2d):
    cls_to_become = Bias2d

    bias: UninitializedParameter  # type: ignore[assignment]

    def __init__(self) -> None:
        super().__init__(0, 0, 0)
        self.bias = UninitializedParameter()

    def materialize(self, shape: Size) -> None:
        self.bias.materialize((1, *shape[1:]))
