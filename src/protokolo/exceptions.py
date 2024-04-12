# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Exception classes."""

from operator import attrgetter
from typing import Any

from .i18n import _


class ProtokoloError(Exception):
    """Common exception class for all custom errors raised by the
    :mod:`protokolo` module.
    """


class DictTypeError(TypeError, ProtokoloError):
    """Expected a value of a different type for a given key."""

    def __init__(self, *args: Any):
        if (args_count := len(args)) > 4:
            raise TypeError(
                _(
                    "Function takes no more than 4 arguments ({args_count}"
                    " given)"
                ).format(args_count=args_count)
            )
        super().__init__(*args)
        self.key: str = self._get_item_default(args, 0)
        self.expected_type: type = self._get_item_default(args, 1)
        self.got: Any = self._get_item_default(args, 2)
        self.source: str = self._get_item_default(args, 3)

    def __str__(self) -> str:
        """Custom str output."""
        amount = len(self.args)
        if amount <= 0:
            return super().__str__()
        text = self._key_text()
        if amount >= 2:
            attrs = [
                attrgetter("__name__"),  # str
                attrgetter("__args__"),  # str | None
                attrgetter("__class__.__name__"),  # "hello"
            ]
            for attr in attrs:
                try:
                    name = attr(self.expected_type)
                    # Get the nice str representation of UnionTypes.
                    if isinstance(name, tuple):
                        name = self.expected_type
                    break
                except AttributeError:
                    continue
            else:
                raise TypeError(
                    _("Expected a type, got {type}").format(
                        type=repr(self.expected_type)
                    )
                )
            text += " "
            text += _("Expected {name}.").format(name=name)
        if amount >= 3:
            text += " "
            text += _("Got {value}.").format(value=repr(self.got))
        if amount >= 4:
            text = _("{source}: {text}").format(source=self.source, text=text)
        return text

    def _key_text(self) -> str:
        return _("'{key}' does not have the correct type.").format(key=self.key)

    @staticmethod
    def _get_item_default(
        args: tuple[Any, ...], index: int, default: Any = None
    ) -> Any:
        try:
            return args[index]
        except IndexError:
            return default


class DictTypeListError(DictTypeError):
    """Like :class:`DictTypeError`, but the item is in a list (inside of a
    dictionary) instead of in a dictionary.
    """

    def _key_text(self) -> str:
        return _(
            "List '{key}' contains an element with the wrong type."
        ).format(key=self.key)


class ProtokoloTOMLError(ProtokoloError):
    """An exception that pertains to ``.protokolo.toml.``"""


class AttributeNotPositiveError(ValueError, ProtokoloTOMLError):
    """A value in :class:`.config.SectionAttributes` is expected to be a
    positive integer.
    """


class ProtokoloTOMLNotFoundError(FileNotFoundError, ProtokoloTOMLError):
    """Couldn't find a ``.protokolo.toml`` file."""


class ProtokoloTOMLIsADirectoryError(IsADirectoryError, ProtokoloTOMLError):
    """``.protokolo.toml`` is not a file."""


class HeadingFormatError(ValueError, ProtokoloError):
    """Could not create heading."""
