# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the formatting code."""

from datetime import date
from inspect import cleandoc

import pytest
from freezegun import freeze_time

from protokolo._formatter import MarkdownFormatter, ReStructuredTextFormatter
from protokolo.config import SectionAttributes
from protokolo.exceptions import HeadingFormatError


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
        with pytest.raises(HeadingFormatError):
            MarkdownFormatter.format_section(
                SectionAttributes(title="", level=1)
            )

    def test_format_section_zero_level(self):
        """A section must have a level."""
        attrs = SectionAttributes(title="Foo", level=1)
        attrs.level = 0
        with pytest.raises(HeadingFormatError):
            MarkdownFormatter.format_section(attrs)

    def test_format_section_negative_level(self):
        """Level cannot be negative."""
        attrs = SectionAttributes(title="Foo", level=1)
        attrs.level = -1
        with pytest.raises(HeadingFormatError):
            MarkdownFormatter.format_section(attrs)

    def test_format_section_format_simple(self):
        """Do additional formatting in the title."""
        assert (
            MarkdownFormatter.format_section(
                SectionAttributes(
                    title="Foo $level $foo", level=1, values={"foo": 2}
                )
            )
            == "# Foo 1 2"
        )
        assert (
            MarkdownFormatter.format_section(
                SectionAttributes(
                    title="Foo ${level} ${foo}", level=1, values={"foo": 2}
                )
            )
            == "# Foo 1 2"
        )

    @freeze_time("2023-11-08")
    def test_format_section_format_date(self):
        """$date is replaced with today's date."""
        assert (
            MarkdownFormatter.format_section(
                SectionAttributes(title="Foo $date", level=1)
            )
            == "# Foo 2023-11-08"
        )

    @freeze_time("2023-11-08")
    def test_format_section_format_date_override(self):
        """If date is defined in the attrs, don't actually use today's date."""
        assert (
            MarkdownFormatter.format_section(
                SectionAttributes(
                    title="Foo $date",
                    level=1,
                    values={"date": date(2023, 10, 25)},
                )
            )
            == "# Foo 2023-10-25"
        )

    def test_format_section_format_missing(self):
        """If a key has no value, don't render it."""
        assert (
            MarkdownFormatter.format_section(
                SectionAttributes(title="Foo $bar", level=1)
            )
            == "# Foo $bar"
        )

    def test_format_section_format_none(self):
        """If a key has value None, don't render it."""
        assert (
            MarkdownFormatter.format_section(
                SectionAttributes(
                    title="Foo $bar", level=1, values={"bar": None}
                )
            )
            == "# Foo $bar"
        )

    def test_format_section_format_title(self):
        """Don't recursively render $title."""
        assert (
            MarkdownFormatter.format_section(
                SectionAttributes(title="Foo $title", level=1)
            )
            == "# Foo $title"
        )


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
        with pytest.raises(HeadingFormatError):
            ReStructuredTextFormatter.format_section(
                SectionAttributes(title="Foo", level=10)
            )

    def test_format_with_replacement(self):
        """The length of the section symbols adjusts to the rendered text."""
        assert ReStructuredTextFormatter.format_section(
            SectionAttributes(title="Foo $bar", level=1, values={"bar": "bar"})
        ) == cleandoc(
            """
            =======
            Foo bar
            =======
            """
        )
