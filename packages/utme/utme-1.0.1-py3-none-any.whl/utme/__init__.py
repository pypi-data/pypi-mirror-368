"""
Universal Turing Machine Emulator.

Abstract types:
- `Alphabet`
- `Tape`
- `Rules`

Elementary data types:
- `Symbol`
- `State`

Structured data types:
- `Match`
- `Act`
- `Input`
- `Output`
- `Machine`

Enumeration data types:
- `Move`

Pre-defined objects:
- `BLANK`

Functions:
- `run`
"""

from __future__ import annotations

from typing import Final

from ._alphabet import Alphabet
from ._input import Input
from ._machine import Machine
from ._output import Output
from ._rules import Act, Match, Move, Rules
from ._runner import run
from ._state import State
from ._symbol import BLANK, Symbol
from ._tape import Tape

__all__: Final = (
    "BLANK",
    "Act",
    "Alphabet",
    "Input",
    "Machine",
    "Match",
    "Move",
    "Output",
    "Rules",
    "State",
    "Symbol",
    "Tape",
    "run",
)

# Package metadata
__version__: Final = "1.0.1"
