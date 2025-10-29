"""Sparv plugin to import CoNLL-U files."""

from . import conllu_import

__all__ = ["conllu_import"]


def hello() -> str:
    """Say hello.

    Examples:
    >>> hello()
    'Hello from sparv-sbx-conllu!'
    """
    return "Hello from sparv-sbx-conllu!"
