# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
from __future__ import annotations

import jax
import jax.numpy as jnp
from jax import ffi

from ._common import _dtype


def indexed_linear(
    A: jax.Array,
    B: jax.Array,
    D: jax.ShapeDtypeStruct,
    counts: jax.Array,
    u: int,
    v: int,
    C: int,
    Z: int,
    subscripts: tuple[str, str, str],
    coefficient: float,
    math_dtype: jnp.dtype,
) -> jax.Array:
    math_dtype = jnp.dtype(math_dtype)
    subscripts = tuple(subscripts)
    original_subscripts = subscripts
    assert len(subscripts) == 3
    swap_u_v = False
    swap_A_B = False

    if subscripts in [("u", "v", "vu"), ("uv", "v", "u"), ("vu", "v", "u")]:
        swap_A_B = True
        swap_u_v = True
    if subscripts in [("v", "uv", "u"), ("v", "vu", "u"), ("v", "u", "vu")]:
        swap_u_v = True
    if subscripts in [("v", "u", "uv"), ("uv", "u", "v"), ("vu", "u", "v")]:
        swap_A_B = True

    if swap_u_v:
        subscripts = tuple(
            x.replace("u", "q").replace("v", "u").replace("q", "v") for x in subscripts
        )
        u, v = v, u

    if swap_A_B:
        subscripts = (subscripts[1], subscripts[0], subscripts[2])
        A, B = B, A

    temp_storage_bytes_cub_ExclusiveSum = 1024  # TODO this seems to be sufficient but we never know if it's enough for all use cases and GPUs
    workspace_size = (
        counts.size * (3 + 1) * jnp.dtype(jnp.int64).itemsize
        + temp_storage_bytes_cub_ExclusiveSum
    )
    workspace = jnp.empty((workspace_size,), dtype=jnp.int8)

    if subscripts == ("u", "v", "uv"):
        (D, _) = ffi.ffi_call("indexed_linear_C", (D, workspace))(
            A,
            B,
            counts,
            math_dtype=_dtype(math_dtype),
            u=u,
            v=v,
            C=C,
            Z=Z,
            coefficient=coefficient,
            dtype_A=_dtype(A.dtype),
            dtype_B=_dtype(B.dtype),
            dtype_D=_dtype(D.dtype),
        )
        return D

    if subscripts == ("u", "uv", "v"):
        transpose_B = False
    elif subscripts == ("u", "vu", "v"):
        transpose_B = True
    else:
        raise ValueError(f"Invalid subscripts: {original_subscripts}.")

    (D, _) = ffi.ffi_call("indexed_linear_B", (D, workspace))(
        A,
        B,
        counts,
        math_dtype=_dtype(math_dtype),
        u=u,
        v=v,
        C=C,
        Z=Z,
        transpose_B=transpose_B,
        coefficient=coefficient,
        dtype_A=_dtype(A.dtype),
        dtype_B=_dtype(B.dtype),
        dtype_D=_dtype(D.dtype),
    )
    return D
