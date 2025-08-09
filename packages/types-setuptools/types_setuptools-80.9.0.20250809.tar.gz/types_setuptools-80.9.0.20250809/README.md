## Typing stubs for setuptools

This is a [PEP 561](https://peps.python.org/pep-0561/) type stub package for
the [`setuptools`](https://github.com/pypa/setuptools) package. It can be used by type checkers
to check code that uses `setuptools`. This version of
`types-setuptools` aims to provide accurate annotations for
`setuptools==80.9.*`.

Given that `pkg_resources` is typed since `setuptools >= 71.1`, it is no longer included with `types-setuptools`.

This package is part of the [typeshed project](https://github.com/python/typeshed).
All fixes for types and metadata should be contributed there.
See [the README](https://github.com/python/typeshed/blob/main/README.md)
for more details. The source for this package can be found in the
[`stubs/setuptools`](https://github.com/python/typeshed/tree/main/stubs/setuptools)
directory.

This package was tested with the following type checkers:
* [mypy](https://github.com/python/mypy/) 1.16.1
* [pyright](https://github.com/microsoft/pyright) 1.1.403

It was generated from typeshed commit
[`91ba0da4aad754c912a82b9e052cb4f8191ce520`](https://github.com/python/typeshed/commit/91ba0da4aad754c912a82b9e052cb4f8191ce520).