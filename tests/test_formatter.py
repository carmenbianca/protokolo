# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the formatting code."""

from inspect import cleandoc

import pytest

from protokolo._formatter import MarkdownFormatter, ReStructuredTextFormatter
from protokolo.exceptions import HeaderFormatError


class TestMarkdownFormatter:
    """Collect all tests for MarkdownFormatter."""

    def test_format_section_one_level(self):
        """Format an h1 section."""
        assert MarkdownFormatter.format_section("Foo", 1) == "# Foo"

    def test_format_section_two_levels(self):
        """Format an h2 section."""
        assert MarkdownFormatter.format_section("Foo", 2) == "## Foo"

    def test_format_section_n_levels(self):
        """Format an hN section."""
        for i in range(1, 10):
            assert (
                MarkdownFormatter.format_section("Foo", i) == "#" * i + " Foo"
            )

    def test_format_section_no_title(self):
        """Cannot format a section without a title."""
        with pytest.raises(HeaderFormatError):
            MarkdownFormatter.format_section("", 1)

    def test_format_section_zero_level(self):
        """A section must have a level."""
        with pytest.raises(HeaderFormatError):
            MarkdownFormatter.format_section("Foo", 0)

    def test_format_section_negative_level(self):
        """Level cannot be negative."""
        with pytest.raises(HeaderFormatError):
            MarkdownFormatter.format_section("Foo", -1)


class TestReStructuredTextFormatter:
    """Collect all tests for ReStructuredTextFormatter."""

    def test_format_section_one_level(self):
        """Format an h1 section."""
        assert ReStructuredTextFormatter.format_section("Foo", 1) == cleandoc(
            """
            ===
            Foo
            ===
            """
        )

    def test_format_section_two_levels(self):
        """Format an h2 section."""
        assert ReStructuredTextFormatter.format_section(
            "Foo Bar Baz", 2
        ) == cleandoc(
            """
            Foo Bar Baz
            ===========
            """
        )

    def test_format_section_three_levels(self):
        """Format an h3 section."""
        assert ReStructuredTextFormatter.format_section(
            "Hello, world", 3
        ) == cleandoc(
            """
            Hello, world
            ------------
            """
        )

    def test_format_section_level_too_deep(self):
        """Very deep sections are not supported."""
        with pytest.raises(HeaderFormatError):
            ReStructuredTextFormatter.format_section("Foo", 10)
