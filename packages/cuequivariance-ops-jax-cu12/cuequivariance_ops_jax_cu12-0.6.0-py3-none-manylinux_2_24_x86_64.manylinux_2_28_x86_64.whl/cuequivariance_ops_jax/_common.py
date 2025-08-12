# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import ctypes
import importlib.metadata
import os
from enum import IntEnum

import jax.numpy as jnp
from jax import ffi

import cuequivariance_ops  # noqa: F401

# Load libcue_ops_jax.so
try:
    dist = importlib.metadata.distribution("cuequivariance_ops_jax")
    root = dist.locate_file("cuequivariance_ops_jax")
except Exception:
    # last resort, will fail with writeable install
    root = os.path.dirname(__file__)

path = os.path.join(root, "lib/libcue_ops_jax.so")
library = ctypes.cdll.LoadLibrary(path)

# Register the c++ functions with JAX
CUSTOM_FUNCS = [
    (
        "tensor_product_uniform_1d_jit",
        "tensor_product_uniform_1d_jit",
        "tensor_product_uniform_1d_cpu",
    ),
    ("indexed_linear_B", "indexed_linear_B", None),
    ("indexed_linear_C", "indexed_linear_C", None),
    ("triangle_attention_cuda_fwd", "triangle_attention_cuda_fwd", None),
    ("triangle_attention_cuda_bwd", "triangle_attention_cuda_bwd", None),
    ("noop", "noop_gpu", "noop_cpu"),
    ("sleep", "sleep_gpu", "sleep_cpu"),
    ("synchronize", "synchronize_gpu", "synchronize_cpu"),
]

for name, cuda_fn, cpu_fn in CUSTOM_FUNCS:
    if cuda_fn is not None:
        ffi.register_ffi_target(
            name=name, fn=ffi.pycapsule(getattr(library, cuda_fn)), platform="CUDA"
        )
    if cpu_fn is not None:
        ffi.register_ffi_target(
            name=name, fn=ffi.pycapsule(getattr(library, cpu_fn)), platform="cpu"
        )


class DataType(IntEnum):
    FLOAT32 = 0
    FLOAT64 = 1
    FLOAT16 = 2
    BFLOAT16 = 3
    INT32 = 4
    INT64 = 5


def _dtype(jax_dtype: jnp.dtype) -> DataType:
    try:
        return {
            jnp.float32: DataType.FLOAT32,
            jnp.float64: DataType.FLOAT64,
            jnp.float16: DataType.FLOAT16,
            jnp.bfloat16: DataType.BFLOAT16,
            jnp.int32: DataType.INT32,
            jnp.int64: DataType.INT64,
        }[jnp.dtype(jax_dtype).type]
    except KeyError:
        raise ValueError(f"Unsupported dtype: {jax_dtype}")
