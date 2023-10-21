# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Code to combine the files in protokolo/ into a single text block."""

from abc import ABC, abstractmethod

# pylint: disable=too-few-public-methods


class MarkupFormatter(ABC):
    """A simple formatter class."""

    @classmethod
    @abstractmethod
    def format_section(cls, title: str, level: int) -> str:
        """Format a title as a section header. For instance, a level-2 Markdown
        section might look like this::

            ## Hello, world

        Raises:
            ValueError: level is 0 or lower.
        """
        if level <= 0:
            raise ValueError(f"level must be positive, but is {level}")
        return title


class MarkdownFormatter(MarkupFormatter):
    """A Markdown formatter."""

    @classmethod
    def format_section(cls, title: str, level: int) -> str:
        super().format_section(title, level)
        pound_signs = f"{'#' * level}"
        if title:
            return f"{pound_signs} {title}"
        return pound_signs
