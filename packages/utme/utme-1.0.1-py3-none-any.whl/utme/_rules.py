from __future__ import annotations

import dataclasses
import enum
from typing import TYPE_CHECKING, Final, final

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ._state import State
    from ._symbol import Symbol

__all__: Final = ("Act", "Match", "Move", "Rules")


# A `Rules` object maps match rules to act rules.
type Rules = Mapping[Match, Act]


@final
@enum.unique
class Move(enum.Enum):
    """A movement command for a Turing machine."""

    LEFT = enum.auto()
    STAY = enum.auto()
    RIGHT = enum.auto()


@final
@dataclasses.dataclass(frozen=True, slots=True)
class Match:
    """
    A match rule.

    It matches when a Turing machine has read the given symbol, when
    the machine is in the given state.
    """

    symbol: Symbol
    state: State


@final
@dataclasses.dataclass(frozen=True, slots=True)
class Act:
    """
    An act rule.

    It commands a Turing machine to write the given symbol in the current cell,
    move the head as specified by `move`, and transition into the given state.
    """

    symbol: Symbol
    move: Move
    state: State
