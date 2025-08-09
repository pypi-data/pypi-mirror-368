from __future__ import annotations

import collections
from typing import TYPE_CHECKING, Final, final

from ._output import Output
from ._rules import Match, Move
from ._symbol import BLANK, Symbol

if TYPE_CHECKING:
    from ._input import Input
    from ._machine import Machine
    from ._tape import Tape

__all__: Final = ("run",)


@final
class _TapeHead:
    # An ever-extending tape-head.

    __slots__ = ("_index", "_tape")

    def __init__(self, tape: Tape, index: int, /) -> None:
        self._tape: Final = collections.deque(tape)

        # Initial "move" is arbitrary step-wise
        self._index = index
        for _ in range(self._index - len(self._tape) + 1):
            self._tape.append(BLANK)

    def export(self, /) -> tuple[Symbol, ...]:
        return tuple(self._tape)

    def read(self, /) -> Symbol:
        return self._tape[self._index]

    def write(self, symbol: Symbol, /) -> None:
        self._tape[self._index] = symbol

    def move(self, move: Move, /) -> None:
        match move:
            case Move.LEFT:
                if self._index < 1:
                    self._tape.appendleft(BLANK)
                else:
                    self._index -= 1
            case Move.RIGHT:
                self._index += 1
                if self._index == len(self._tape):
                    self._tape.append(BLANK)
            # NOTE (pragma): `coverage` does not understand (yet) that this is
            # an exhaustive match.
            case Move.STAY:  # pragma: no cover
                pass


@final
class _RunningMachine:
    # A "materialized" Turing machine.

    __slots__ = ("_state", "_tapehead", "halting_states", "rules")

    def __init__(self, machine: Machine, input_: Input, /) -> None:
        if frozenset(input_.tape) - frozenset(machine.alphabet):
            _msg = "Given tape contains symbols outside the alphabet"
            raise ValueError(_msg)

        self.rules: Final = machine.rules
        self.halting_states: Final = machine.halting_states
        self._tapehead: Final = _TapeHead(input_.tape, input_.initial_index)

        self._state = machine.initial_state

    def step(self, /) -> Output | None:
        current = Match(symbol=self._tapehead.read(), state=self._state)
        if current not in self.rules:
            _msg = f"No match for: {current}"
            raise RuntimeError(_msg)

        act = self.rules[current]
        self._tapehead.write(act.symbol)
        self._tapehead.move(act.move)
        self._state = act.state

        if self._state in self.halting_states:
            return Output(tape=self._tapehead.export(), state=self._state)
        return None


def run(*, machine: Machine, input_: Input) -> Output:
    """
    Run the given machine with the given input, and return the output.

    NOTE: If the machine wouldn't halt, neither would this function.
    """
    running_machine = _RunningMachine(machine, input_)
    while (output := running_machine.step()) is None:
        pass
    return output
