# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""The global configuration of Protokolo."""

import tomllib
from collections.abc import Sequence
from copy import deepcopy
from pathlib import Path
from types import UnionType
from typing import IO, Any, Self, cast

import attrs

from ._util import nested_itemgetter, type_in_expected_type
from .exceptions import (
    AttributeNotPositiveError,
    DictTypeError,
    DictTypeListError,
)
from .types import StrPath, TOMLValue, TOMLValueType


def parse_toml(
    toml: str | IO[bytes],
    section: Sequence[str] | None = None,
) -> dict[str, Any]:
    """
    Args:
        toml: A TOML string or binary file object.
        sections: A list of nested sections, for example
            ``["protokolo", "section"]`` to return the values of
            ``[protokolo.section]``

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


@attrs.define
class TOMLConfig:
    """A utility class to hold data parsed from a TOML file."""

    _values: dict[str, TOMLValue] = attrs.field(factory=dict)
    source: str | None = attrs.field(converter=str, default=None)

    def __attrs_post_init__(self) -> None:
        self._values = deepcopy(self._values)
        # Can't use validator on the attribute itself because the validation
        # depends on `self`. So we do the validation here.
        self.validate()

    @classmethod
    def from_dict(
        cls, values: dict[str, Any], source: StrPath | None = None
    ) -> Self:
        """Generate :class:`TOMLConfig` from a dictionary containing the keys
        and values. This is useless for the :class:`TOMLConfig` base class, but
        potentially useful for subclasses that change the ``__init__``
        signature.

        Raises:
            DictTypeError: value isn't an expected/supported type.
            DictTypeListError: if a list contains elements other than a dict.
        """
        return cls(values=values, source=str(source))

    def __getitem__(self, key: str | Sequence[str]) -> TOMLValue:
        if isinstance(key, str):
            keys = [key]
        else:
            keys = list(key)
        return nested_itemgetter(*keys)(self._values)

    def __setitem__(self, key: str | Sequence[str], value: TOMLValue) -> None:
        if isinstance(key, str):
            final_key = key
            keys = []
        else:
            copied = list(key)
            final_key = copied.pop()
            keys = copied
        nested_itemgetter(*keys)(self._values)[final_key] = value

    def as_dict(self) -> dict[str, TOMLValue]:
        """Return a mapping of the :class:`TOMLConfig`."""
        return deepcopy(self._values)

    def validate(self) -> None:
        """Verify that all keys contain valid TOML types. This is automatically
        run on object instantiation.

        Raises:
            DictTypeError: value isn't an expected/supported type.
            DictTypeListError: if a list contains elements other than a dict.
        """
        self._validate(cast(dict[str, Any], self._values))

    def _validate(self, values: dict[str, Any]) -> None:
        for name, value in values.items():
            # Use typed annotations to expect a very specific type. If not,
            # allow any valid TOML type.
            # pylint: disable=no-member
            expected_type = self.__annotations__.get(f"_{name}", TOMLValueType)
            self._validate_item(value, name, expected_type=expected_type)
            if isinstance(value, dict):
                self._validate(value)
            elif isinstance(value, list):
                self._validate_list(value, name)

    def _validate_item(
        self,
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
            raise DictTypeError(name, expected_type, item, str(self.source))

    def _validate_list(
        self,
        values: list[Any],
        name: str,
    ) -> None:
        for item in values:
            if isinstance(item, dict):
                self._validate(item)
            elif isinstance(item, list):
                self._validate_list(item, name)
            else:
                try:
                    self._validate_item(item, name)
                except DictTypeError as error:
                    raise DictTypeListError(
                        name, TOMLValueType, item, self.source
                    ) from error


@attrs.define
class SectionAttributes(TOMLConfig):
    """A data container to hold some metadata for a :class:`.compile.Section`
    object.
    """

    _title: str = attrs.field(
        default="TODO: No section title defined",
        repr=False,
        eq=False,
        order=False,
    )
    _level: int = attrs.field(default=1, repr=False, eq=False, order=False)
    _order: int | None = attrs.field(
        default=None, repr=False, eq=False, order=False
    )

    def __attrs_post_init__(self) -> None:
        self._values = deepcopy(self._values)
        # The private variables are no longer used after they are written to
        # _values.
        self._values.setdefault("title", self._title)
        self._values.setdefault("level", self._level)
        self._values.setdefault("order", self._order)
        super().__attrs_post_init__()

    @classmethod
    def from_dict(
        cls, values: dict[str, Any], source: StrPath | None = None
    ) -> Self:
        """Generate :class:`SectionAttributes` from a dictionary containing the
        keys and values.

        Raises:
            AttributeNotPositiveError: one of the values should have been
                positive.
            DictTypeError: value isn't an expected/supported type.
            DictTypeListError: if a list contains elements other than a dict.
        """
        return super().from_dict(values, source=source)

    def validate(self) -> None:
        """
        Raises:
            AttributeNotPositiveError: one of the values should have been
                positive.
            DictTypeError: value isn't an expected/supported type.
            DictTypeListError: if a list contains elements other than a dict.
        """
        super().validate()
        if self.level <= 0:
            raise AttributeNotPositiveError(
                f"level must be a positive integer, got {repr(self.level)}"
            )
        if self.order is not None and self.order <= 0:
            raise AttributeNotPositiveError(
                f"order must be None or a positive integer, got"
                f" {repr(self.order)}"
            )

    @property
    def title(self) -> str:
        """The title of a section. If no value is provided, it defaults to
        'TODO: No section title defined'.
        """
        return cast(str, self["title"])

    @title.setter
    def title(self, value: str) -> None:
        self["title"] = value

    @property
    def level(self) -> int:
        """The level of the section heading, which must not be zero or lower."""
        return cast(int, self["level"])

    @level.setter
    def level(self, value: int) -> None:
        self["level"] = value

    @property
    def order(self) -> int | None:
        """The order of the section in relation to others. It must not be zero
        or lower, and may be :const:`None`, in which case it is alphabetically
        sorted after all sections that do have an order.
        """
        return cast(int | None, self["order"])

    @order.setter
    def order(self, value: int | None) -> None:
        self["order"] = value


@attrs.define
class GlobalConfig(TOMLConfig):
    """A container object for config values of the global ``.protokolo.toml``
    file.
    """

    _changelog: str | None = attrs.field(
        default=None, repr=False, eq=False, order=False
    )
    _markup: str | None = attrs.field(
        default=None, repr=False, eq=False, order=False
    )
    _directory: str | None = attrs.field(
        default=None, repr=False, eq=False, order=False
    )

    _FILE_SECTION = {
        ".protokolo.toml": ["protokolo"],
        "pyproject.toml": ["tool", "protokolo"],
    }

    def __attrs_post_init__(self) -> None:
        self._values = deepcopy(self._values)
        self._values.setdefault("changelog", self._changelog)
        self._values.setdefault("markup", self._markup)
        self._values.setdefault("directory", self._directory)
        super().__attrs_post_init__()

    @classmethod
    def from_file(cls, path: StrPath) -> Self:
        """Factory method to create a :class:`GlobalConfig` from a path. The
        exact table that is loaded from the file depends on the file name. In
        ``pyproject.toml``, the table ``[tool.protokolo]`` is loaded, whereas
        ``[protokolo]`` is loaded everywhere else.

        Raises:
            OSError: if the file could not be opened.
            tomllib.TOMLDecodeError: if the file could not be decoded.
            DictTypeError: value isn't an expected/supported type.
            DictTypeListError: if a list contains elements other than a dict.
        """
        path = Path(path)
        section = cls._FILE_SECTION.get(path.name, ["protokolo"])
        with path.open("rb") as fp:
            try:
                values = parse_toml(fp, section=section)
            except tomllib.TOMLDecodeError as error:
                raise tomllib.TOMLDecodeError(
                    f"Invalid TOML in '{fp.name}': {error}"
                ) from error
        return cls.from_dict(values, source=path)

    @classmethod
    def find_config(cls, directory: StrPath) -> Path | None:
        """In *directory*, find the config file.

        The order of precedence (highest to lowest) is:

        - ``.protokolo.toml``
        - ``pyproject.toml``
        """
        directory = Path(directory)
        for name in cls._FILE_SECTION:
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
