"""Compatibility layer"""

import sys

if sys.version_info < (3, 10):  # pragma: no cover
    from typing_extensions import TypeAlias, TypeGuard
else:  # pragma: no cover
    from typing import TypeAlias, TypeGuard

if sys.version_info < (3, 11):  # pragma: no cover
    from typing_extensions import Concatenate, NotRequired, ParamSpec, TypedDict, Unpack
else:  # pragma: no cover
    from typing import Concatenate, NotRequired, ParamSpec, TypedDict, Unpack


__all__ = [
    "Concatenate",
    "NotRequired",
    "ParamSpec",
    "TypeAlias",
    "TypeGuard",
    "TypedDict",
    "Unpack",
]
