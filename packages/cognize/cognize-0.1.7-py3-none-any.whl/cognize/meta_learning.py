# Licensed under the Apache License, Version 2.0
# -*- coding: utf-8 -*-
"""
cognize.meta_learning
=====================

Thin façade over the kernel's policy machinery with a small bounds DSL.

Why this file exists
--------------------
- Keep a single source of truth for PolicySpec / PolicyMemory / ShadowRunner / PolicyManager
  (they live in `cognize.epistemic`).
- Provide a lightweight ParamRange/ParamSpace helper for bounded evolution and a
  convenience adapter to wire it into the kernel's EpistemicState.

Public API
----------
- Re-exports (from cognize.epistemic):
    PolicySpec, PolicyMemory, ShadowRunner, PolicyManager, EpistemicState
- Bounds DSL:
    ParamRange, ParamSpace
- Helper:
    enable_evolution(state, space, every=30, rate=1.0, margin=1.02)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Any

# Single-source the core types from the kernel (no duplication here)
from .epistemic import (
    PolicySpec,
    PolicyMemory,
    ShadowRunner,
    PolicyManager,
    EpistemicState,
)


# ---------------------------------------------------------------------
# Bounds DSL (maps to PolicyManager.set_param_space expected format)
# ---------------------------------------------------------------------

@dataclass
class ParamRange:
    """
    Inclusive numeric range with optional relative mutation scale (sigma ∈ [0,1]).
    Used for evolvable parameters like k, Θ, a, sigma, step_cap, decay_rate, epsilon.

    Example:
        ParamRange(0.05, 0.40, 0.08)
    """
    low: float
    high: float
    sigma: float = 0.05

    def __post_init__(self) -> None:
        self.low = float(self.low)
        self.high = float(self.high)
        self.sigma = float(max(0.0, min(1.0, self.sigma)))
        if self.high < self.low:
            raise ValueError("ParamRange.high must be >= low")

    def as_tuple(self) -> tuple[float, float, float]:
        """Kernel-accepted tuple representation: (low, high, sigma)."""
        return (self.low, self.high, self.sigma)

    def __repr__(self) -> str:
        return f"ParamRange(low={self.low}, high={self.high}, sigma={self.sigma})"


class ParamSpace:
    """
    Mapping: policy_id -> param_name -> ParamRange

    Example:
        space = ParamSpace().set({
            "cautious": {"k": ParamRange(0.05, 0.4, 0.08), "a": ParamRange(0.01, 0.2, 0.05)},
            "adoptive": {"k": ParamRange(0.10, 0.5)}
        })
    """
    def __init__(self, space: Optional[Dict[str, Dict[str, ParamRange]]] = None):
        self._space: Dict[str, Dict[str, ParamRange]] = space or {}

    def set(self, space: Dict[str, Dict[str, ParamRange]]) -> "ParamSpace":
        self._space = space
        return self

    def update(self, space: Dict[str, Dict[str, ParamRange]]) -> "ParamSpace":
        for pid, params in (space or {}).items():
            self._space.setdefault(pid, {}).update(params)
        return self

    def to_kernel(self) -> Dict[str, Dict[str, Any]]:
        """
        Convert to the kernel-accepted shape for PolicyManager.set_param_space:
            {policy_id: {param: (low, high, sigma)}}
        """
        out: Dict[str, Dict[str, Any]] = {}
        for pid, params in self._space.items():
            out[pid] = {}
            for k, pr in params.items():
                if not isinstance(pr, ParamRange):
                    raise TypeError(f"ParamSpace[{pid}][{k}] must be ParamRange")
                out[pid][k] = pr.as_tuple()
        return out

    def is_empty(self) -> bool:
        return not any(self._space.values())

    def __bool__(self) -> bool:
        return not self.is_empty()

    def __repr__(self) -> str:
        policies = ", ".join(self._space.keys()) or "∅"
        counts = {pid: len(ps) for pid, ps in self._space.items()}
        return f"ParamSpace(policies=[{policies}], params={counts})"


# ---------------------------------------------------------------------
# Convenience wiring
# ---------------------------------------------------------------------

def enable_evolution(
    state: EpistemicState,
    space: ParamSpace,
    every: int = 30,
    rate: float = 1.0,
    margin: float = 1.02,
) -> None:
    """
    Convenience wrapper around EpistemicState.enable_auto_evolution.

    Preconditions:
      - `state` has a PolicyManager attached (state.policy_manager is not None).
      - `space` is a ParamSpace with per-policy ParamRange bounds.

    Effects:
      - Configures the state's PolicyManager with bounds and cadence.
      - Enables safe, bounded parameter mutation + promotion via kernel logic.
    """
    if not isinstance(state, EpistemicState):
        raise TypeError("state must be an EpistemicState")
    if not isinstance(space, ParamSpace):
        raise TypeError("space must be a ParamSpace")
    if not state.policy_manager or not isinstance(state.policy_manager, PolicyManager):
        raise ValueError("EpistemicState needs a PolicyManager attached before enabling evolution.")
    state.enable_auto_evolution(space.to_kernel(), every=every, rate=rate, margin=margin)


__all__ = [
    # façaded kernel types (single source of truth)
    "PolicySpec",
    "PolicyMemory",
    "ShadowRunner",
    "PolicyManager",
    "EpistemicState",
    # bounds DSL + helper
    "ParamRange",
    "ParamSpace",
    "enable_evolution",
]

