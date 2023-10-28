# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""The global configuration of Protokolo."""

import contextlib
import tomllib
from collections.abc import Sequence
from types import UnionType
from typing import IO, Any, Self, cast

from ._util import nested_itemgetter, type_in_expected_type
from .exceptions import DictTypeError, DictTypeListError
from .types import NestedTypeDict, TOMLValue, TOMLValueType


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


class TOMLConfig:
    """A utility class to hold data parsed from a TOML file."""

    _expected_types: NestedTypeDict = {}

    def __init__(self, **kwargs: TOMLValue):
        self._config = kwargs
        self.validate()

    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> Self:
        """Generate TOMLConfig from a dictionary containing the keys and
        values.

        Raises:
            DictTypeError: value types are wrong.
        """
        return cls(**values)

    def __getitem__(self, key: str | Sequence[str]) -> TOMLValue:
        if isinstance(key, str):
            keys = [key]
        else:
            keys = list(key)
        return nested_itemgetter(*keys)(self._config)

    def __setitem__(self, key: str | Sequence[str], value: TOMLValue) -> None:
        if isinstance(key, str):
            final_key = key
            keys = []
        else:
            copied = list(key)
            final_key = copied.pop()
            keys = copied
        # Technically this can fail because self._config is a Mapping instead of
        # a MutableMetting.
        nested_itemgetter(*keys)(self._config)[final_key] = value

    def validate(self) -> None:
        """TODO.

        Raises:
            DictTypeError: value isn't an expected/supported type.
            DictTypeListError: if a list contains elements other than a dict.
        """
        self._validate(cast(dict[str, Any], self._config))

    @classmethod
    def _validate(
        cls, values: dict[str, Any], path: Sequence[str] | None = None
    ) -> None:
        if path is None:
            path = []
        for name, value in values.items():
            expected_type: UnionType = TOMLValueType
            with contextlib.suppress(KeyError):
                expected_type = nested_itemgetter(*(list(path) + [name]))(
                    cls._expected_types
                )
            cls._validate_item(value, name, expected_type=expected_type)
            if isinstance(value, dict):
                cls._validate(value, path=list(path) + [name])
            elif isinstance(value, list):
                for item in value:
                    if not isinstance(item, dict):
                        raise DictTypeListError(name, dict, item)
                    cls._validate(item, path=list(path) + [name])

    @classmethod
    def _validate_item(
        cls,
        item: Any,
        name: str,
        expected_type: type | UnionType = TOMLValueType,
    ) -> None:
        # Because `isinstance(False, int)` is True, but we want it to be False,
        # we do some custom magic here to achieve that effect.
        bool_err = False
        if isinstance(item, bool) and not type_in_expected_type(
            bool, expected_type
        ):
            bool_err = True
        if bool_err or not isinstance(item, expected_type):
            raise DictTypeError(name, expected_type, item)


class Config:
    """A container object for config values of the global .protokolo.toml."""

    def __init__(self, config: dict[str, str] | None = None):
        if config is None:
            config = {}
        self._config = config

    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> Self:
        """Generate Config from a dictionary containing the keys and values."""
        return cls(values)

    @classmethod
    def from_file(cls) -> Self:
        """TODO"""
        return cls()

    @classmethod
    def from_directory(cls) -> Self:
        """TODO"""
        return cls()
