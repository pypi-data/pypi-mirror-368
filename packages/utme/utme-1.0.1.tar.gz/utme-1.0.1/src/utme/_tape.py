from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ._symbol import Symbol

__all__: Final = ("Tape",)


# Covers input and output tapes for Turing machines.
type Tape = Sequence[Symbol]
