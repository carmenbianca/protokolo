# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Code to combine the files in ``changelog.d/`` into a single text block."""

import errno
import tomllib
from io import StringIO
from itertools import chain
from operator import attrgetter
from os import strerror
from pathlib import Path, PurePath
from typing import Iterator, Self, cast

import attrs as attrs_
from attrs.converters import optional

from ._formatter import MARKUP_EXTENSION_MAPPING as _MARKUP_EXTENSION_MAPPING
from ._formatter import MARKUP_FORMATTER_MAPPING as _MARKUP_FORMATTER_MAPPING
from .config import SectionAttributes, parse_toml
from .exceptions import (
    AttributeNotPositiveError,
    HeadingFormatError,
    ProtokoloTOMLIsADirectoryError,
    ProtokoloTOMLNotFoundError,
)
from .i18n import _
from .types import StrPath, SupportedMarkup

# pylint: disable=too-few-public-methods


@attrs_.define(frozen=True)
class Fragment:
    """A fragment, analogous to a file."""

    text: str
    source: PurePath | None = attrs_.field(
        default=None, converter=optional(PurePath)
    )

    def compile(self) -> str:
        """Compile the fragment. For the time being, this just means adding a
        newline at the end if one does not exist.
        """
        if not self.text.endswith("\n"):
            return f"{self.text}\n"
        return self.text


@attrs_.define(eq=False)
class Section:
    """A section, analogous to a directory."""

    attrs: SectionAttributes = attrs_.field(factory=SectionAttributes)
    markup: SupportedMarkup = "markdown"
    source: PurePath | None = attrs_.field(
        default=None, converter=optional(PurePath)
    )

    fragments: set[Fragment] = attrs_.field(factory=set, init=False)
    subsections: set[Self] = attrs_.field(factory=set, init=False)

    @classmethod
    def from_directory(
        cls,
        directory: StrPath,
        level: int = 1,
        markup: SupportedMarkup = "markdown",
        section_format_pairs: dict[str, str] | None = None,
    ) -> Self:
        """Factory method to recursively create a :class:`Section` from a
        directory.

        Args:
            directory: The changelog.d directory.
            level: The level of the root :class:`Section`. This is overridden by
                the level value in ``.protokolo.toml``, if any.
            markup: The markup language.
            section_format_pairs: Additional key-value pairs used to format the
                section headings, applied recursively to all subsections.

        Raises:
            OSError: input/output error.
            ProtokoloTOMLNotFoundError: ``.protokolo.toml`` doesn't exist.
            ProtokoloTOMLIsADirectoryError: ``.protokolo.toml`` is not a file.
            tomllib.TOMLDecodeError: ``.protokolo.toml`` couldn't be parsed.
            DictTypeError: ``.protokolo.toml`` fields have the wrong type.
            AttributeNotPositiveError: value in ``.protokolo.toml`` should be a
                positive integer.
        """
        if section_format_pairs is None:
            section_format_pairs = {}

        directory = Path(directory)
        section = cls(markup=markup, source=directory)

        section._load_section_attributes(directory, level, section_format_pairs)
        section._load_subsections_and_fragments(
            directory, section.attrs.level, section_format_pairs
        )

        return section

    def _load_section_attributes(
        self, directory: Path, level: int, section_format_pairs: dict[str, str]
    ) -> None:
        """Locate ``.protokolo.toml`` and create a :class:`SectionAttributes`
        object from it, then set that object on self.

        Raises:
            OSError: input/output error.
            ProtokoloTOMLNotFoundError: ``.protokolo.toml`` doesn't exist.
            ProtokoloTOMLIsADirectoryError: ``.protokolo.toml`` is not a file.
            tomllib.TOMLDecodeError: ``.protokolo.toml`` couldn't be parsed.
        """
        protokolo_toml = directory / ".protokolo.toml"
        if not protokolo_toml.exists():
            raise ProtokoloTOMLNotFoundError(
                errno.ENOENT, strerror(errno.ENOENT), str(protokolo_toml)
            )
        if not protokolo_toml.is_file():
            raise ProtokoloTOMLIsADirectoryError(
                errno.EISDIR, strerror(errno.EISDIR), str(protokolo_toml)
            )
        with protokolo_toml.open("rb") as fp:
            try:
                values = parse_toml(fp, section=["protokolo", "section"])
            except tomllib.TOMLDecodeError as error:
                raise tomllib.TOMLDecodeError(
                    _("Invalid TOML in {file_name}: {error}").format(
                        file_name=repr(fp.name), error=error
                    )
                ) from error
        try:
            attrs = SectionAttributes.from_dict(values, source=fp.name)
        except AttributeNotPositiveError as error:
            raise AttributeNotPositiveError(
                _("Wrong value in {file_name}: {error}").format(
                    file_name=repr(fp.name), error=error
                )
            ) from error
        # The level of the current section is determined first by the value
        # in the toml, second by the level value.
        level = values.get("level") or level
        attrs.level = level
        for key, val in section_format_pairs.items():
            attrs[key] = val
        self.attrs = attrs

    def _load_subsections_and_fragments(
        self, directory: Path, level: int, section_format_pairs: dict[str, str]
    ) -> None:
        """Locate subsections and fragments. Load fragments onto self, and
        recursively create subsections to also load them onto self.

        Raises:
            OSError: input/output error.
            ProtokoloTOMLNotFoundError: ``.protokolo.toml`` doesn't exist.
            ProtokoloTOMLIsADirectoryError: ``.protokolo.toml`` is not a file.
            tomllib.TOMLDecodeError: ``.protokolo.toml`` couldn't be parsed.
            DictTypeError: ``.protokolo.toml`` fields have the wrong type.
            AttributeNotPositiveError: value in ``.protokolo.toml`` should be a
                positive integer.
        """
        subsections = set()
        fragments = set()
        for path in directory.iterdir():
            if path.is_dir() and (path / ".protokolo.toml").is_file():
                subsections.add(
                    self.from_directory(
                        path,
                        level=level + 1,
                        markup=self.markup,
                        section_format_pairs=section_format_pairs,
                    )
                )
            elif (
                path.is_file()
                and path.suffix in _MARKUP_EXTENSION_MAPPING[self.markup]
            ):
                with path.open("r", encoding="utf-8") as fp_:
                    content = fp_.read()
                    fragments.add(Fragment(text=content, source=path))
        self.subsections = cast(set[Self], subsections)
        self.fragments = fragments

    def compile(self) -> str:
        """Compile the entire section recursively, first printing the fragments
        in order, then the subsections.

        Empty sections are not compiled.

        Raises:
            HeadingFormatError: could not format heading of section.
        """
        buffer = self.write_to_buffer()
        return buffer.getvalue()

    def write_to_buffer(self, buffer: StringIO | None = None) -> StringIO:
        """Like compile, but writing to a :class:`StringIO` buffer.

        Raises:
            HeadingFormatError: could not format heading of section.
        """
        if buffer is None:
            buffer = StringIO()

        if self.is_empty():
            return buffer

        try:
            heading = _MARKUP_FORMATTER_MAPPING[self.markup].format_section(
                self.attrs,
            )
        except HeadingFormatError as error:
            raise HeadingFormatError(
                _(
                    "Failed to format section heading of {source}: {error}"
                ).format(source=repr(str(self.source)), error=str(error))
            ) from error
        buffer.write(heading)
        buffer.write("\n")

        if self.fragments:
            buffer.write("\n")
        for fragment in self.sorted_fragments():
            buffer.write(fragment.compile())

        for subsection in self.sorted_subsections():
            if not subsection.is_empty():
                buffer.write("\n")
            subsection.write_to_buffer(buffer=buffer)

        return buffer

    def is_empty(self) -> bool:
        """A :class:`Section` is empty if it contains neither fragments nor
        subsections. If it contains no fragments, and its subsections are empty,
        then it is also considered empty.
        """
        if self.fragments:
            return False
        if not self.subsections:
            return True
        for subsection in self.subsections:
            if not subsection.is_empty():
                return False
        return True

    def sorted_fragments(self) -> Iterator[Fragment]:
        """Yield the fragments, ordered by their source. Fragments that do not
        have a source are sorted afterwards by their text.
        """
        with_source = {
            fragment
            for fragment in self.fragments
            if fragment.source is not None
        }
        source_sorted = sorted(
            with_source,
            key=lambda fragment: cast(PurePath, fragment.source).stem,
        )
        alphabetical_sorted = sorted(
            self.fragments - with_source, key=attrgetter("text")
        )
        return chain(source_sorted, alphabetical_sorted)

    def sorted_subsections(self) -> Iterator[Self]:
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
