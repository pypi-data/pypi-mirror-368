Universal Turing Machine Emulator
=================================

**utme** is a library that provides [*Turing machine*][tm] emulation in pure
Python.

With **utme**, you can define a *Turing machine*, run it with an input and
inspect its output.

> Note: I wrote this library to help myself understand Turing machines.
> **utme** is not suitable for efficient/performant Turing machine emulation.

[tm]: https://en.wikipedia.org/wiki/Turing_machine

### Why is it called *universal*?

As the library allows you to define any valid *Turing machine* (universal or
not) and run it, the library itself is equivalent to a *universal Turing
machine* (a Turing machine that accepts another Turing machine and an input for
it, and yields its output).

While **utme** does not emulate a universal Turing machine by itself, I found
the name cool (It was originally `utm`, but then I found out it was already
taken by another project on [PyPI][pypi]).

That said, there is an [example script](./examples/universal.py) that
composes `universal_machine`; a universal Turing machine using **utme**.
The script also provides `encode`/`decode` functions that converts **utme**
objects from and into valid tapes for `universal_machine` (so you can even pass
`universal_machine` (with an input) to itself!).

[pypi]: https://pypi.org/


Installation
------------

**utme** is available in the [Python Package Index][pypi-utme]:

```sh
pip install utme
```

The library has zero dependencies and should work on any Python (3.12+)
implementation on any platform.

[pypi-utme]: https://pypi.org/project/utme/


Documentation
-------------

**utme**'s API is documented at the definition level (via *docstrings* where
possible, and comments otherwise).

The library code is around 250 logical line of codes, so you can easily read
the source code to understand implementation details.

Exported objects are categorized and enumerated briefly in the package's
*docstring*:

```sh
python -m pydoc utme
```

### Examples

Examples of Turing machines implemented using **utme** are included in the
[examples](./examples) directory.


Development
-----------

You only need [`uv`][uv] and [`just`][just] on your POSIX system to get
started.

Run `just` (without arguments) to see available tasks.

[uv]: https://github.com/astral-sh/uv
[just]: https://github.com/casey/just

### Contribution

Before you submit a patch, please run `just precommit` and make sure the task
runs successfully.  Patches that don't pass `just precommit` will not be
merged.


License
-------

**utme** is licensed under the [MIT (Expat) license](./LICENSE).

> Copyright (C) 2025 Karam Assany (karam.assany@disroot.org)
