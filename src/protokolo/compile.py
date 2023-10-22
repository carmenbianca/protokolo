# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Code to combine the files in protokolo/ into a single text block."""

import tomllib
from io import StringIO
from itertools import chain
from operator import attrgetter
from pathlib import Path
from typing import IO, Any, Iterator, cast

from ._formatter import MarkdownFormatter
from ._util import StrPath

# pylint: disable=too-few-public-methods


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
        if level <= 0:
            raise ValueError("level must be a positive integer")
        self.level: int = level
        if order is not None and order <= 0:
            raise ValueError("order must be None or a positive integer")
        self.order: int | None = order
        self.other: dict[str, str] = kwargs

    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> "SectionAttributes":
        """Generate SectionAttributes from a dictionary containing the keys and
        values.

        Raises:
            ValueError: value types are wrong.
        """
        values = values.copy()
        # We do some type validation here, assuming that the dictionary contains
        # user input.
        title = values.pop("title", None)
        if title is not None:
            cls._validate_str(title, "title")
        level = values.pop("level", 1)
        if level is not None:
            cls._validate_int(level, "level")
        if level is None:
            # Sneaky.
            level = 1
        order = values.pop("order", None)
        if order is not None:
            cls._validate_int(order, "order")
        for name, value in values.items():
            cls._validate_str(value, name)
        return cls(
            title=title,
            level=level,
            order=order,
            **values,
        )

    @classmethod
    def from_toml(cls, toml: str | IO[bytes]) -> "SectionAttributes":
        """Parse a TOML string or file into a SectionAttributes object.

        Raises:
            ValueError: [protokolo.section] is missing, value types are wrong,
                or *toml* is not a valid type.
            tomllib.TOMLDecodeError: not valid TOML.
        """
        values = cls.parse_toml(toml)
        return cls.from_dict(values)

    @staticmethod
    def parse_toml(toml: str | IO[bytes]) -> dict[str, Any]:
        """
        Raises:
            ValueError: [protokolo.section] is missing, value types are wrong,
                or *toml* is not a valid type.
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
                raise ValueError("toml must be a str or IO[bytes]") from error
        try:
            subdict = values["protokolo"]["section"]
        except KeyError as error:
            raise ValueError(
                "Table [protokolo.section] does not exist in TOML"
            ) from error
        return subdict

    @staticmethod
    def _validate_int(value: Any, name: str) -> None:
        """
        Raises:
            ValueError: value isn't an int.
        """
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"{name} must be an integer, but is {type(value)}")

    @staticmethod
    def _validate_str(value: Any, name: str) -> None:
        """
        Raises:
            ValueError: value isn't a str.
        """
        if not isinstance(value, str):
            raise ValueError(f"{name} must be a string, but is {type(value)}")


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
    def from_directory(cls, directory: StrPath, level: int = 1) -> "Section":
        """Factory method to recursively create a Section from a directory.

        The *level* keyword argument is overridden by the level value in
        .protokolo.toml.
        """
        directory = Path(directory)
        protokolo_toml = directory / ".protokolo.toml"
        if protokolo_toml.exists() and protokolo_toml.is_file():
            with protokolo_toml.open("rb") as fp:
                values = SectionAttributes.parse_toml(fp)
            attrs = SectionAttributes.from_dict(values)
            # The level of the current section is determined first by the value
            # in the toml, second by the level value.
            level = values.get("level") or level
            attrs.level = level
        else:
            # TODO: Log warning, probably.
            attrs = SectionAttributes(level=level)

        subsections = set()
        entries = set()
        for path in directory.iterdir():
            if path.is_dir():
                subsections.add(cls.from_directory(path, level=level + 1))
            # TODO: Handle more suffixes
            elif path.is_file() and path.suffix == ".md":
                with path.open("r", encoding="utf-8") as fp:
                    content = fp.read()
                    entries.add(Entry(text=content, source=path))

        section = cls(attrs=attrs, source=directory)
        section.subsections = subsections
        section.entries = entries

        return section

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
        buffer.write(
            MarkdownFormatter.format_section(self.attrs.title, self.attrs.level)
        )

        for entry in self.sorted_entries():
            buffer.write("\n\n")
            buffer.write(entry.compile())

        for subsection in self.sorted_subsections():
            buffer.write("\n\n")
            subsection.write_to_buffer(buffer=buffer)

        return buffer

    def sorted_entries(self) -> Iterator["Entry"]:
        """Yield the entries, ordered by their source. Entries that do not have
        a source are sorted afterwards by their text.
        """
        with_source = {
            entry for entry in self.entries if entry.source is not None
        }
        source_sorted = sorted(
            with_source, key=lambda entry: cast(Path, entry.source).name
        )
        alphabetical_sorted = sorted(
            self.entries - with_source, key=attrgetter("text")
        )
        return chain(source_sorted, alphabetical_sorted)

    def sorted_subsections(self) -> Iterator["Section"]:
        """Yield the subsections, first ordered by their order value, then the
        remainder sorted alphabetically.
        """
        with_order = {
            section
            for section in self.subsections
            if section.attrs.order is not None
        }
        ordered_sorted = sorted(
            with_order,
            key=attrgetter("attrs.order", "attrs.title"),
        )
        alphabetical_sorted = sorted(
            self.subsections - with_order,
            key=attrgetter("attrs.title"),
        )
        return chain(ordered_sorted, alphabetical_sorted)


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
