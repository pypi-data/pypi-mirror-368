from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Final, final

if TYPE_CHECKING:
    from ._tape import Tape

__all__: Final = ("Input",)


@final
@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class Input:
    """
    A Turing machine input: the initial tape and an initial index.

    The initial index determines which cell of the tape to initially put the
    head on, counting from zero, left-to-right (default is zero i.e. the first
    cell).
    """

    tape: Tape
    initial_index: int = 0

    def __post_init__(self, /) -> None:
        if self.initial_index < 0:
            _msg = "Initial index must be a natural number"
            raise ValueError(_msg)
