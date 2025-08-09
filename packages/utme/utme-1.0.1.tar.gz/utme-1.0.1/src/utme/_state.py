from __future__ import annotations

import dataclasses
from typing import Final, final

__all__: Final = ("State",)


@final
@dataclasses.dataclass(frozen=True, slots=True)
class State:
    """
    A Turing machine state.

    States have associated "code" values to separate qualitative identity
    (`==`) from numerical identity (`is)`, making it easier to copy/pickle
    states and objects composed of them.
    """

    code: str
