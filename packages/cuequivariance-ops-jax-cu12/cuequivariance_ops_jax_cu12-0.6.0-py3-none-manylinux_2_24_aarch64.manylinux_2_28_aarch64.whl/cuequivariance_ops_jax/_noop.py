# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
"""No-op FFI function that returns inputs unchanged."""

from typing import Any

import jax
import jax.numpy as jnp
from jax import ffi


def _flatten(pytree: Any):
    """Helper to apply FFI function to JAX arrays in a pytree."""
    leaves, treedef = jax.tree.flatten(pytree)
    arrays = [(i, leaf) for i, leaf in enumerate(leaves) if isinstance(leaf, jax.Array)]
    _, values = zip(*arrays)

    def unflatten(outputs):
        for idx, (leaf_idx, _) in enumerate(arrays):
            leaves[leaf_idx] = outputs[idx]
        return jax.tree.unflatten(treedef, leaves)

    return values, unflatten


def noop(pytree: Any) -> Any:
    """
    No-op function that returns input pytree unchanged through FFI.

    Args:
        pytree: Any pytree structure containing JAX arrays

    Returns:
        The same pytree structure with arrays passed through FFI
    """
    vals, unflatten = _flatten(pytree)

    vals = ffi.ffi_call(
        "noop",
        [jax.ShapeDtypeStruct(arr.shape, arr.dtype) for arr in vals],
        input_output_aliases={i: i for i in range(len(vals))},
    )(*vals)

    return unflatten(vals)


def sleep(seconds: jax.Array, pytree: Any) -> tuple[jax.Array, Any]:
    """
    Sleep for the specified number of seconds and return input pytree unchanged.

    Args:
        seconds: Number of seconds to sleep (as a JAX array)
        pytree: Any pytree structure containing JAX arrays

    Returns:
        A tuple of (elapsed_ticks, pytree) where elapsed_ticks is the number of
        clock ticks that elapsed during the sleep operation
    """
    seconds = jnp.asarray(seconds, dtype=jnp.float32)
    vals, unflatten = _flatten(pytree)

    outputs = ffi.ffi_call(
        "sleep",
        [jax.ShapeDtypeStruct((), jnp.int64)]
        + [jax.ShapeDtypeStruct(arr.shape, arr.dtype) for arr in vals],
        input_output_aliases={i: i for i in range(1, len(vals) + 1)},
    )(seconds, *vals)
    elapsed_ticks, vals = outputs[0], outputs[1:]

    return elapsed_ticks, unflatten(vals)


def synchronize(pytree: Any) -> tuple[jax.Array, Any]:
    """
    Synchronize the current CUDA stream and return input pytree unchanged.

    Args:
        pytree: Any pytree structure containing JAX arrays

    Returns:
        A tuple of (elapsed_seconds, pytree) where elapsed_seconds is the time
        in seconds it took to synchronize the CUDA stream
    """
    vals, unflatten = _flatten(pytree)

    outputs = ffi.ffi_call(
        "synchronize",
        [jax.ShapeDtypeStruct((), jnp.float32)]
        + [jax.ShapeDtypeStruct(arr.shape, arr.dtype) for arr in vals],
        input_output_aliases={i: i + 1 for i in range(len(vals))},
    )(*vals)
    elapsed_seconds, vals = outputs[0], outputs[1:]

    return elapsed_seconds, unflatten(vals)
