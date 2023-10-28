# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""The global configuration of Protokolo."""

import contextlib
import tomllib
from collections.abc import Sequence
from pathlib import Path
from types import UnionType
from typing import IO, Any, Self, cast

from ._util import nested_itemgetter, type_in_expected_type
from .exceptions import DictTypeError, DictTypeListError
from .types import NestedTypeDict, StrPath, TOMLValue, TOMLValueType


def parse_toml(
    toml: str | IO[bytes],
    section: Sequence[str] | None = None,
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
    if not section:
        return values
    try:
        return nested_itemgetter(*section)(values)
    except KeyError:
        return {}


class TOMLConfig:
    """A utility class to hold data parsed from a TOML file."""

    expected_types: NestedTypeDict = {}

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

    def _validate(
        self, values: dict[str, Any], path: Sequence[str] | None = None
    ) -> None:
        if path is None:
            path = []
        for name, value in values.items():
            expected_type: UnionType = TOMLValueType
            with contextlib.suppress(KeyError):
                expected_type = nested_itemgetter(*(list(path) + [name]))(
                    self.expected_types
                )
            self._validate_item(value, name, expected_type=expected_type)
            if isinstance(value, dict):
                self._validate(value, path=list(path) + [f"{name}+dict"])
            elif isinstance(value, list):
                for item in value:
                    if not isinstance(item, dict):
                        raise DictTypeListError(name, dict, item)
                    self._validate(item, path=list(path) + [f"{name}+list"])

    @staticmethod
    def _validate_item(
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


class GlobalConfig(TOMLConfig):
    """A container object for config values of the global .protokolo.toml."""

    expected_types = {"changelog": str, "markup": str, "directory": str}

    _file_section = {
        ".protokolo.toml": ["protokolo"],
        "pyproject.toml": ["tool", "protokolo"],
    }

    def __init__(
        self,
        changelog: str | None = None,
        markup: str | None = None,
        directory: str | None = None,
        **kwargs: TOMLValue,
    ):
        kwargs["changelog"] = changelog
        kwargs["markup"] = markup
        kwargs["directory"] = directory
        super().__init__(**kwargs)

    @classmethod
    def from_file(cls, path: StrPath) -> Self:
        """Factory method to create a GlobalConfig from a path. The exact table
        that is loaded from the file depends on the file name. In
        pyproject.toml, the table [tool.protokolo] is loaded, whereas
        [protokolo] is loaded everywhere else.
        """
        path = Path(path)
        section = cls._file_section.get(path.name, ["protokolo"])
        with path.open("rb") as fp:
            try:
                values = parse_toml(fp, section=section)
            except tomllib.TOMLDecodeError as error:
                raise tomllib.TOMLDecodeError(
                    f"Invalid TOML in '{fp.name}': {error}"
                ) from error
        return cls(**values)

    @classmethod
    def find_config(cls, directory: StrPath) -> Path | None:
        """In *directory*, find the config file.

        The order of precedence (highest to lowest) is:

        - .protokolo.toml
        - pyproject.toml
        """
        directory = Path(directory)
        for name in cls._file_section:
            target = directory / name
            if target.exists() and target.is_file():
                return target
        return None

    @property
    def changelog(self) -> str | None:
        """The path to CHANGELOG."""
        return cast(str | None, self["changelog"])

    @changelog.setter
    def changelog(self, value: str | None) -> None:
        self["changelog"] = value

    @property
    def markup(self) -> str | None:
        """The markup language used by the project."""
        return cast(str | None, self["markup"])

    @markup.setter
    def markup(self, value: str | None) -> None:
        self["markup"] = value

    @property
    def directory(self) -> str | None:
        """The directory where the change log entries are stored."""
        return cast(str | None, self["directory"])

    @directory.setter
    def directory(self, value: str | None) -> None:
        self["directory"] = value
