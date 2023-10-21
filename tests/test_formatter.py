# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the formatting code."""

from inspect import isclass

import pytest

from protokolo import _formatter
from protokolo._formatter import MarkdownFormatter, MarkupFormatter

formatter_classes = [
    cls
    for cls in _formatter.__dict__.values()
    if isclass(cls)
    and issubclass(cls, MarkupFormatter)
    and cls is not MarkupFormatter
]


@pytest.fixture(scope="session", params=formatter_classes)
def formatter(request):
    """Return a formatter class."""
    yield request.param


class TestMarkupFormatter:
    """Collect all tests for MarkupFormatter."""

    def test_format_section_zero_level(self, formatter):
        """Level cannot be 0."""
        with pytest.raises(ValueError):
            formatter.format_section("Foo", 0)

    def test_format_section_minus_one_level(self, formatter):
        """Level cannot be negative."""
        with pytest.raises(ValueError):
            formatter.format_section("Foo", -1)


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

    def test_format_section_zero_level(self):
        """Level cannot be 0."""
        with pytest.raises(ValueError):
            MarkdownFormatter.format_section("Foo", 0)

    def test_format_section_minus_one_level(self):
        """Level cannot be negative."""
        with pytest.raises(ValueError):
            MarkdownFormatter.format_section("Foo", -1)
