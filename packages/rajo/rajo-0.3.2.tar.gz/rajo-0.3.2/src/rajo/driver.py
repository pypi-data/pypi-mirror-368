__all__ = ['get_gpu_capability', 'get_gpu_memory_info']

import os
from collections.abc import Iterator
from contextlib import contextmanager
from typing import NamedTuple

import pynvml
from glow import si_bin


@contextmanager
def _nvml() -> Iterator[None]:
    pynvml.nvmlInit()
    try:
        yield
    finally:
        pynvml.nvmlShutdown()


def _get_device_handles() -> list:
    devices = os.environ.get('CUDA_VISIBLE_DEVICES')
    indices = (
        range(int(pynvml.nvmlDeviceGetCount()))
        if devices is None
        else map(int, devices.split(','))
    )
    return [pynvml.nvmlDeviceGetHandleByIndex(i) for i in indices]


class _GpuState(NamedTuple):
    free: list[int]
    total: list[int]


def get_gpu_capability() -> list[tuple[int, int]]:
    """Gives CUDA capability for each GPU"""
    with _nvml():
        handles = _get_device_handles()
        return [pynvml.nvmlDeviceGetCudaComputeCapability(h) for h in handles]


def get_gpu_memory_info() -> _GpuState:
    """Gives size of free and total VRAM memory for each GPU"""
    with _nvml():
        handles = _get_device_handles()
        infos = [pynvml.nvmlDeviceGetMemoryInfo(h) for h in handles]

    return _GpuState(
        [si_bin(i.free) for i in infos], [si_bin(i.total) for i in infos]
    )
