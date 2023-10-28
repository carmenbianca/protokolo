# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Some miscellaneous utilities."""

from collections.abc import Callable, Mapping
from typing import Any


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
