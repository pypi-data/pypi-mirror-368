## Typing stubs for uWSGI

This is a [PEP 561](https://peps.python.org/pep-0561/) type stub package for
the [`uWSGI`](https://github.com/unbit/uwsgi) package. It can be used by type checkers
to check code that uses `uWSGI`. This version of
`types-uWSGI` aims to provide accurate annotations for
`uWSGI==2.0.*`.

Type hints for uWSGI's [Python API](https://uwsgi-docs.readthedocs.io/en/latest/PythonModule.html). Note that this API is available only when running Python code inside a uWSGI process and some parts of the API are only present when corresponding configuration options have been enabled.

This package is part of the [typeshed project](https://github.com/python/typeshed).
All fixes for types and metadata should be contributed there.
See [the README](https://github.com/python/typeshed/blob/main/README.md)
for more details. The source for this package can be found in the
[`stubs/uWSGI`](https://github.com/python/typeshed/tree/main/stubs/uWSGI)
directory.

This package was tested with the following type checkers:
* [mypy](https://github.com/python/mypy/) 1.16.1
* [pyright](https://github.com/microsoft/pyright) 1.1.403

It was generated from typeshed commit
[`91ba0da4aad754c912a82b9e052cb4f8191ce520`](https://github.com/python/typeshed/commit/91ba0da4aad754c912a82b9e052cb4f8191ce520).