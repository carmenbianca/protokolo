# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Code to combine the files in protokolo/ into a single text block."""

from abc import ABC, abstractmethod

# pylint: disable=too-few-public-methods


class MarkupLanguage(ABC):
    """A simple formatter class."""

    @classmethod
    @abstractmethod
    def format_section(cls, title: str, level: int) -> str:
        """Format a title as a section header. For instance, a level-2 Markdown
        section might look like this::

            ## Hello, world
        """


class Section:
    """A section, analogous to a directory."""

    def __init__(
        self,
        level: int = 1,
        attrs: dict[str, str] | None = None,
        source: str | None = None,
    ):
        self.level = level
        if attrs is None:
            attrs = {}
        self.attrs: dict[str, str] = attrs
        self.source: str | None = source
        self.entries: list[Entry] = []
        self.subsections: list[Section] = []
        # TODO: order

    @classmethod
    def from_directory(cls, directory: str) -> "Section":
        """Factory method to recursively create a Section from a directory."""
        # TODO
        print(directory)
        return cls()

    @property
    def title(self) -> str:
        """Get the title from attrs."""
        if not (result := self.attrs.get("title")):
            result = "TODO: No section title defined"
        return result.format(**self.attrs)

    def compile(self) -> str:
        """Compile the entire section recursively, first printing the entries in
        order, then the subsections.
        """
        return "TODO"


class Entry:
    """An entry, analogous to a file."""

    def __init__(self, text: str, source: str | None = None):
        self.text: str = text
        self.source: str | None = source
