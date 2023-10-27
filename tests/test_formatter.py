# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the formatting code."""

from protokolo._formatter import MarkdownFormatter


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
        """Format a section without a title."""
        assert MarkdownFormatter.format_section("", 1) == "#"
