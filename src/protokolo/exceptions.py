# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Exception classes."""

from typing import Any


class ProtokoloError(Exception):
    """Common exception class for all custom errors raised by protokolo."""


class DictTypeError(TypeError, ProtokoloError):
    """Expected a value of a different type for a given key."""

    def __init__(self, *args: Any):
        if (args_count := len(args)) > 4:
            raise TypeError(
                f"Function takes no more than 4 arguments ({args_count} given)"
            )
        super().__init__(*args)
        self.key = self._get_item_default(args, 0)
        self.expected_type = self._get_item_default(args, 1)
        self.got = self._get_item_default(args, 2)
        self.source = self._get_item_default(args, 3)

    def __str__(self) -> str:
        """Custom str output."""
        if self.key is None:
            return super().__str__()
        text = f"{repr(self.key)} does not have the correct type."
        if self.expected_type:
            try:
                name = self.expected_type.__name__
            except AttributeError:
                name = self.expected_type.__class__.__name__
            text += f" Expected {name}."
        if self.got:
            text += f" Got {repr(self.got)}."
        if self.source:
            text = f"{self.source}: {text}"
        return text

    @staticmethod
    def _get_item_default(
        args: tuple[Any, ...], index: int, default: Any = None
    ) -> Any:
        try:
            return args[index]
        except IndexError:
            return default


class ProtokoloTOMLError(ProtokoloError):
    """An exception that pertains to .protokolo.toml."""


class AttributeNotPositiveError(ValueError, ProtokoloTOMLError):
    """A value in AttributeSections is expected to be a positive integer."""


class ProtokoloTOMLNotFoundError(FileNotFoundError, ProtokoloTOMLError):
    """Couldn't find a .protokolo.toml file."""


class ProtokoloTOMLIsADirectoryError(IsADirectoryError, ProtokoloTOMLError):
    """.protokolo.toml is not a file."""
