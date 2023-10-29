# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the formatting code."""

from inspect import cleandoc

import pytest

from protokolo._formatter import MarkdownFormatter, ReStructuredTextFormatter
from protokolo.config import SectionAttributes
from protokolo.exceptions import HeaderFormatError


class TestMarkdownFormatter:
    """Collect all tests for MarkdownFormatter."""

    def test_format_section_one_level(self):
        """Format an h1 section."""
        assert (
            MarkdownFormatter.format_section(
                SectionAttributes(title="Foo", level=1)
            )
            == "# Foo"
        )

    def test_format_section_two_levels(self):
        """Format an h2 section."""
        assert (
            MarkdownFormatter.format_section(
                SectionAttributes(title="Foo", level=2)
            )
            == "## Foo"
        )

    def test_format_section_n_levels(self):
        """Format an hN section."""
        for i in range(1, 10):
            assert (
                MarkdownFormatter.format_section(
                    SectionAttributes(title="Foo", level=i)
                )
                == "#" * i + " Foo"
            )

    def test_format_section_no_title(self):
        """Cannot format a section without a title."""
        with pytest.raises(HeaderFormatError):
            MarkdownFormatter.format_section(
                SectionAttributes(title="", level=1)
            )

    def test_format_section_zero_level(self):
        """A section must have a level."""
        attrs = SectionAttributes(title="Foo", level=1)
        attrs.level = 0
        with pytest.raises(HeaderFormatError):
            MarkdownFormatter.format_section(attrs)

    def test_format_section_negative_level(self):
        """Level cannot be negative."""
        attrs = SectionAttributes(title="Foo", level=1)
        attrs.level = -1
        with pytest.raises(HeaderFormatError):
            MarkdownFormatter.format_section(attrs)


class TestReStructuredTextFormatter:
    """Collect all tests for ReStructuredTextFormatter."""

    def test_format_section_one_level(self):
        """Format an h1 section."""
        assert ReStructuredTextFormatter.format_section(
            SectionAttributes(title="Foo", level=1)
        ) == cleandoc(
            """
            ===
            Foo
            ===
            """
        )

    def test_format_section_two_levels(self):
        """Format an h2 section."""
        assert ReStructuredTextFormatter.format_section(
            SectionAttributes(title="Foo Bar Baz", level=2)
        ) == cleandoc(
            """
            Foo Bar Baz
            ===========
            """
        )

    def test_format_section_three_levels(self):
        """Format an h3 section."""
        assert ReStructuredTextFormatter.format_section(
            SectionAttributes(title="Hello, world", level=3)
        ) == cleandoc(
            """
            Hello, world
            ------------
            """
        )

    def test_format_section_level_too_deep(self):
        """Very deep sections are not supported."""
        with pytest.raises(HeaderFormatError):
            ReStructuredTextFormatter.format_section(
                SectionAttributes(title="Foo", level=10)
            )
