from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Collection

    from ._symbol import Symbol

__all__: Final = ("Alphabet",)


# Represents a finite set of symbols that a given Turing machine can recognize.
type Alphabet = Collection[Symbol]
# NOTE: `BLANK` is implicitly considered a member in any alphabet.
