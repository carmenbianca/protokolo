# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""The global configuration of Protokolo."""

import tomllib
from collections.abc import Sequence
from typing import IO, Any

from ._util import nested_itemgetter, validate_str


def parse_toml(
    toml: str | IO[bytes],
    sections: Sequence[str] | None = None,
) -> dict[str, Any]:
    """
    Args:
        toml: A TOML string or binary file object.
        sections: A list of nested sections, for example
            ["protokolo", "section"] to return the values of [protokolo.section]

    Raises:
        TypeError: *toml* is not a valid type.
        tomllib.TOMLDecodeError: not valid TOML.
    """
    if isinstance(toml, str):
        values = tomllib.loads(toml)
    else:
        try:
            values = tomllib.load(toml)
        except tomllib.TOMLDecodeError:
            raise
        except Exception as error:
            raise TypeError("toml must be a str or IO[bytes]") from error
    if not sections:
        return values
    try:
        return nested_itemgetter(*sections)(values)
    except KeyError:
        return {}


class Config:
    """A container object for config values of the global .protokolo.toml."""

    def __init__(self, config: dict[str, str] | None = None):
        if config is None:
            config = {}
        self._config = config

    @classmethod
    def from_dict(cls, values: dict[str, str]) -> "Config":
        """TODO"""
        for name, value in values.items():
            validate_str(value, name)
        return cls(values)

    @classmethod
    def from_file(cls) -> "Config":
        """TODO"""
        return cls()

    @classmethod
    def from_directory(cls) -> "Config":
        """TODO"""
        return cls()
