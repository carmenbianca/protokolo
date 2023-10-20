# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Code to combine the files in protokolo/ into a single text block."""

from abc import ABC, abstractmethod
from io import StringIO
from pathlib import Path

from ._util import StrPath

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


class SectionAttributes:
    """A data container to hold some metadata for a Section."""

    def __init__(
        self,
        title: str | None = None,
        level: int = 1,
        order: int | None = None,
        **kwargs: str,
    ):
        if title is None:
            title = "TODO: No section title defined"
        self.title: str = title
        self.level: int = level
        self.order: int | None = order
        self.other: dict[str, str] = kwargs


class Section:
    """A section, analogous to a directory."""

    def __init__(
        self,
        attrs: SectionAttributes | None = None,
        source: StrPath | None = None,
    ):
        if attrs is None:
            attrs = SectionAttributes()
        self.attrs: SectionAttributes = attrs
        if source is not None:
            source = Path(source)
        self.source: Path | None = source
        self.entries: set[Entry] = set()
        self.subsections: set[Section] = set()

    @classmethod
    def from_directory(cls, directory: str) -> "Section":
        """Factory method to recursively create a Section from a directory."""
        # TODO
        print(directory)
        return cls()

    def compile(self) -> str:
        """Compile the entire section recursively, first printing the entries in
        order, then the subsections.
        """
        buffer = self.write_to_buffer()
        return buffer.getvalue()

    def write_to_buffer(self, buffer: StringIO | None = None) -> StringIO:
        """Like compile, but writing to a StringIO buffer."""
        if buffer is None:
            buffer = StringIO()

        # TODO: Make this nicer obviously.
        buffer.write(self.attrs.level * "#")
        buffer.write(" ")
        buffer.write(self.attrs.title)

        for entry in self.entries:
            buffer.write("\n\n")
            buffer.write(entry.compile())

        for subsection in self.subsections:
            buffer.write("\n\n")
            subsection.write_to_buffer(buffer=buffer)

        return buffer


class Entry:
    """An entry, analogous to a file."""

    def __init__(self, text: str, source: StrPath | None = None):
        self.text: str = text
        if source is not None:
            source = Path(source)
        self.source: Path | None = source

    def compile(self) -> str:
        """Compile the entry. For the time being, this just means stripping the
        newline characters around the text.
        """
        return self.text.strip("\n")
