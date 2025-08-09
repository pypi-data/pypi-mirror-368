from __future__ import annotations

import dataclasses
import warnings
from typing import TYPE_CHECKING, Final, final

from ._symbol import BLANK

if TYPE_CHECKING:
    from collections.abc import Collection

    from ._alphabet import Alphabet
    from ._rules import Rules
    from ._state import State

__all__: Final = ("Machine",)


@final
@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class Machine:
    """A Turing machine description."""

    alphabet: Alphabet
    rules: Rules
    initial_state: State
    halting_states: Collection[State]

    def __post_init__(self, /) -> None:
        alphabet = frozenset((*self.alphabet, BLANK))
        halting_states = frozenset(self.halting_states)

        match_symbols = frozenset(match.symbol for match in self.rules)
        act_symbols = frozenset(act.symbol for act in self.rules.values())
        match_states = frozenset(match.state for match in self.rules)
        act_states = frozenset(act.state for act in self.rules.values())

        # Err if not all match rules' symbols are in the alphabet
        if match_symbols - alphabet:
            _msg = "Given match rules contain symbols outside the alphabet"
            raise ValueError(_msg)

        # Err if not all act rules' symbols are in the alphabet
        if act_symbols - alphabet:
            _msg = "Given act rules contain symbols outside the alphabet"
            raise ValueError(_msg)

        # Err if there is no match rule for the initial state
        if self.initial_state not in match_states:
            _msg = "No match rule matchs initial state"
            raise ValueError(_msg)

        # Err if there is not an act rule for each halting state
        if halting_states - act_states:
            _msg = "One or more halting states with no matching act rule"
            raise ValueError(_msg)

        # Warn if the alphabet contains anything besides BLANK
        if not self.alphabet:
            warnings.warn("Machine with blank-only alphabet", stacklevel=2)

        # Warn if a match rule matches a halting state
        if halting_states & match_states:
            warnings.warn(
                "One or more match rules matches a halting state", stacklevel=2
            )
