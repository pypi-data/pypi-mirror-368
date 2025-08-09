from __future__ import annotations

import dataclasses
from typing import Final, final

__all__: Final = ("BLANK", "Symbol")


@final
@dataclasses.dataclass(frozen=True, slots=True)
class Symbol:
    """
    A symbol for a Turing machine.

    Symbols have associated one-letter "code" values for the following reasons:

    (1) To separate qualitative identity (`==`) from numerical identity (`is`),
    making it easier to copy/pickle symbols and objects composed of them.

    (2) To make it easy to convert tapes into strings and vice versa.
    """

    code: str

    def __post_init__(self, /) -> None:
        if len(self.code) != 1:
            _msg = "Symbols must have 1-character codes"
            raise ValueError(_msg)


# Represents the default symbol on an infinite tape.
BLANK: Final = Symbol(" ")
