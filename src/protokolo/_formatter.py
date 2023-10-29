# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Code to combine the files in protokolo/ into a single text block."""

from abc import ABC, abstractmethod
from inspect import cleandoc

from .config import SectionAttributes
from .exceptions import HeaderFormatError

# pylint: disable=too-few-public-methods


class MarkupFormatter(ABC):
    """A simple formatter class."""

    @classmethod
    @abstractmethod
    def format_section(cls, attrs: SectionAttributes) -> str:
        """Format a title as a section header. For instance, a level-2 Markdown
        section might look like this::

            ## Hello, world

        Raises:
            HeaderFormatError: could not format the header as given.
        """
        # This is technically invalid. Valid attrs do not have a non-positive
        # level.
        if attrs.level <= 0:
            raise HeaderFormatError(f"Level {attrs.level} must be positive.")
        if not attrs.title:
            raise HeaderFormatError("title cannot be empty.")
        return ""


class MarkdownFormatter(MarkupFormatter):
    """A Markdown formatter."""

    @classmethod
    def format_section(cls, attrs: SectionAttributes) -> str:
        super().format_section(attrs)
        pound_signs = f"{'#' * attrs.level}"
        return f"{pound_signs} {attrs.title}"


class ReStructuredTextFormatter(MarkupFormatter):
    """A reStructuredText formatter."""

    # TODO: Honestly this should be more flexible, but the amount of engineering
    # it would take to achieve that is beyond the scope of what I want to do.
    # What were the designers of reST thinking when they didn't define the
    # header hierarchy?
    _levels = {
        1: "=",  # Special case.
        2: "=",
        3: "-",
        4: "~",
        5: "^",
        6: "'",
    }

    @classmethod
    def format_section(cls, attrs: SectionAttributes) -> str:
        super().format_section(attrs)
        try:
            sign = cls._levels[attrs.level]
        except KeyError as error:
            raise HeaderFormatError(
                f"Header level {attrs.level} is too deep."
            ) from error
        length = len(attrs.title)
        return cleandoc(
            f"""
            {sign * length if attrs.level == 1 else ''}
            {attrs.title}
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
