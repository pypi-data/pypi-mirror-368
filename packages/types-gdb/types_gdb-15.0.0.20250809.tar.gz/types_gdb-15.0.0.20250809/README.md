## Typing stubs for gdb

This is a [PEP 561](https://peps.python.org/pep-0561/) type stub package for
the [`gdb`](https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git;a=tree) package. It can be used by type checkers
to check code that uses `gdb`. This version of
`types-gdb` aims to provide accurate annotations for
`gdb==15.0.*`.

Type hints for GDB's [Python API](https://sourceware.org/gdb/onlinedocs/gdb/Python-API.html). Note that this API is available only when running Python scripts under GDB: it is not possible to install the `gdb` package separately, for instance using `pip`.

This package is part of the [typeshed project](https://github.com/python/typeshed).
All fixes for types and metadata should be contributed there.
See [the README](https://github.com/python/typeshed/blob/main/README.md)
for more details. The source for this package can be found in the
[`stubs/gdb`](https://github.com/python/typeshed/tree/main/stubs/gdb)
directory.

This package was tested with the following type checkers:
* [mypy](https://github.com/python/mypy/) 1.16.1
* [pyright](https://github.com/microsoft/pyright) 1.1.403

It was generated from typeshed commit
[`91ba0da4aad754c912a82b9e052cb4f8191ce520`](https://github.com/python/typeshed/commit/91ba0da4aad754c912a82b9e052cb4f8191ce520).