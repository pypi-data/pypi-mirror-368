from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Final, final

if TYPE_CHECKING:
    from ._state import State
    from ._tape import Tape

__all__: Final = ("Output",)


@final
@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class Output:
    """A Turing machine output: the final tape and the state it halted on."""

    tape: Tape
    state: State
