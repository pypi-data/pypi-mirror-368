"""
Compatibility shim: core entities moved into submodules under entities/core/.
This file re-exports the previous public API to avoid breaking imports.
"""

from .core import (  # type: ignore[F401]
    FISH_RIGHT,
    FISH_LEFT,
    FISH_RIGHT_MASKS,
    FISH_LEFT_MASKS,
    random_fish_frames,
    Seaweed,
    Bubble,
    Splat,
    Fish,
)

__all__ = [
    "FISH_RIGHT",
    "FISH_LEFT",
    "FISH_RIGHT_MASKS",
    "FISH_LEFT_MASKS",
    "random_fish_frames",
    "Seaweed",
    "Bubble",
    "Splat",
    "Fish",
]
