# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Some miscellaneous utilities."""

from collections.abc import Callable, Mapping
from typing import Any

from .exceptions import DictTypeError


def nested_itemgetter(*items: Any) -> Callable[[Mapping[Any, Any]], Any]:
    """A nested implementation of operator.itemgetter.

    >>> config = {"hello": {"world": "foo"}}
    >>> nested_itemgetter("hello", "world")(config)
    'foo'

    Raises:
        KeyError: if any of the items doesn't exist in the nested structure.
    """

    def browse(values: Mapping[Any, Any]) -> Any:
        for item in items:
            values = values[item]
        return values

    return browse


def validate_int(value: Any, name: str) -> None:
    """
    Raises:
        DictTypeError: value isn't an int.
    """
    if not isinstance(value, int) or isinstance(value, bool):
        raise DictTypeError(name, int, value)


def validate_str(value: Any, name: str) -> None:
    """
    Raises:
        DictTypeError: value isn't a str.
    """
    if not isinstance(value, str):
        raise DictTypeError(name, str, value)
