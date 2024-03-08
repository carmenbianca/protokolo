# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Some miscellaneous utilities."""

from collections.abc import Callable, Mapping
from inspect import cleandoc as _cleandoc
from types import UnionType
from typing import Any


def type_in_expected_type(value: type, expected_type: type | UnionType) -> bool:
    """Check whether the type *value* matches any of *expected_type*.

    >>> type_in_expected_type(int, int)
    True
    >>> type_in_expected_type(str, str | bytes)
    True
    >>> type_in_expected_type(str, float | int)
    False
    """
    return (isinstance(expected_type, type) and value is expected_type) or (
        isinstance(expected_type, UnionType) and value in expected_type.__args__
    )


def nested_itemgetter(*path: Any) -> Callable[[Mapping[Any, Any]], Any]:
    """A nested implementation of operator.itemgetter.

    >>> config = {"hello": {"world": "foo"}}
    >>> nested_itemgetter("hello", "world")(config)
    'foo'

    Raises:
        KeyError: if any of the path items doesn't exist in the nested
            structure.
    """

    def browse(values: Mapping[Any, Any]) -> Any:
        for item in path:
            values = values[item]
        return values

    return browse


def cleandoc(text: str) -> str:
    """Like :func:`inspect.cleandoc`, but with a newline at the end."""
    return _cleandoc(text) + "\n"
