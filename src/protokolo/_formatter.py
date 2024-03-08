# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Code to combine the files in protokolo/ into a single text block."""

from abc import ABC, abstractmethod
from datetime import date
from inspect import cleandoc
from string import Template
from typing import cast

from .config import SectionAttributes
from .exceptions import HeadingFormatError

# pylint: disable=too-few-public-methods


class MarkupFormatter(ABC):
    """A simple formatter class."""

    @classmethod
    def format_section(cls, attrs: SectionAttributes) -> str:
        """Format a title as a section heading. For instance, a level-2 Markdown
        section might look like this::

            ## Hello, world

        You can use ``$key`` (or ``${key}``) placeholders in the title to
        replace them with the values of the corresponding keys in *attrs*.
        ``$date`` is special in that it is replaced with today's date. ``$$`` is
        replaced by a single ``$``.

        Raises:
            HeadingFormatError: could not format the heading as given.

        """
        cls._validate(attrs)
        title = cls._format_output(attrs)
        return cls._format_section(title, attrs)

    @classmethod
    def _validate(cls, attrs: SectionAttributes) -> None:
        """
        Raises:
            HeadingFormatError: could not format the heading as given.
        """
        # This is technically invalid. Valid attrs do not have a non-positive
        # level.
        if attrs.level <= 0:
            raise HeadingFormatError(f"Level {attrs.level} must be positive.")
        if not attrs.title:
            raise HeadingFormatError("title cannot be empty.")

    @classmethod
    @abstractmethod
    def _format_section(cls, title: str, attrs: SectionAttributes) -> str: ...

    @classmethod
    def _format_output(cls, attrs: SectionAttributes) -> str:
        values = attrs.as_dict()
        # No recursive funny stuff.
        title = cast(str, values.pop("title"))
        # Don't render None.
        values = {
            key: value for key, value in values.items() if value is not None
        }
        values.setdefault("date", date.today())
        template = Template(title)
        return template.safe_substitute(**values)


class MarkdownFormatter(MarkupFormatter):
    """A Markdown formatter."""

    @classmethod
    def _format_section(cls, title: str, attrs: SectionAttributes) -> str:
        pound_signs = f"{'#' * attrs.level}"
        return f"{pound_signs} {title}"


class ReStructuredTextFormatter(MarkupFormatter):
    """A reStructuredText formatter."""

    # TODO: Honestly this should be more flexible, but the amount of engineering
    # it would take to achieve that is beyond the scope of what I want to do.
    # What were the designers of reST thinking when they didn't define the
    # heading hierarchy?
    _levels = {
        1: "=",  # Special case.
        2: "=",
        3: "-",
        4: "~",
        5: "^",
        6: "'",
    }

    @classmethod
    def _validate(cls, attrs: SectionAttributes) -> None:
        super()._validate(attrs)
        if attrs.level > len(cls._levels):
            raise HeadingFormatError(
                f"Heading level {attrs.level} is too deep."
            )

    @classmethod
    def _format_section(cls, title: str, attrs: SectionAttributes) -> str:
        sign = cls._levels[attrs.level]
        length = len(title)
        return cleandoc(
            f"""
            {sign * length if attrs.level == 1 else ''}
            {title}
            {sign * length}
            """
        )


MARKUP_FORMATTER_MAPPING = {
    "markdown": MarkdownFormatter,
    "restructuredtext": ReStructuredTextFormatter,
}

MARKUP_EXTENSION_MAPPING = {
    "markdown": {".md", ".markdown", ""},
    "restructuredtext": {".rst"},
}
