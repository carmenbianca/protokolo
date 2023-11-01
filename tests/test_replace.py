# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the find-and-insert code."""

from inspect import cleandoc

from protokolo.replace import find_first_occurrence, insert_into_str


class TestInsertIntoStr:
    """Collect all tests for insert_into_str."""

    def test_insert_into_str_simple(self):
        """Simple case."""
        target = cleandoc(
            """
            Line 1
            Line 2
            Line 3
            """
        )
        expected = cleandoc(
            """
            Line 1
            Line 2
            Foo
            Line 3
            """
        )
        assert insert_into_str("Foo", target, 2) == expected

    def test_insert_into_str_multiple_lines(self):
        """Insert multiple lines into a string."""
        target = cleandoc(
            """
            Line 1
            Line 2
            """
        )
        expected = cleandoc(
            """
            Line 1
            Foo
            Bar
            Line 2
            """
        )
        assert (
            insert_into_str(
                cleandoc(
                    """
                    Foo
                    Bar
                    """
                ),
                target,
                1,
            )
            == expected
        )

    def test_insert_into_str_target_empty(self):
        """Insert into an empty target."""
        target = ""
        expected = "Foo"
        assert insert_into_str("Foo", target, 0) == expected

    def test_insert_into_str_text_empty(self):
        """Insert empty string into target."""
        target = cleandoc(
            """
            Line 1
            Line 2
            """
        )
        expected = target
        assert insert_into_str("", target, 1) == expected

    def test_insert_into_str_end(self):
        """Insert at the end of the target."""
        target = cleandoc(
            """
            Line 1
            Line 2
            """
        )
        expected = cleandoc(
            """
            Line 1
            Line 2
            Foo
            """
        )
        assert insert_into_str("Foo", target, 2) == expected

    def test_insert_into_str_start(self):
        """Insert at the start of the target."""
        target = cleandoc(
            """
            Line 1
            Line 2
            """
        )
        expected = cleandoc(
            """
            Foo
            Line 1
            Line 2
            """
        )
        assert insert_into_str("Foo", target, 0) == expected


class TestFindFirstOccurrence:
    """Collect all tests for find_first_occurrence."""

    def test_find_first_occurrence_simple(self):
        """Simple case."""
        source = cleandoc(
            """
            Line 1
            Line 2 hello world
            Line 3
            """
        )
        assert find_first_occurrence("hello world", source) == 2

    def test_find_first_occurrence_none(self):
        """There is no occurrence of the text."""
        source = cleandoc(
            """
            Line 1
            Line 2
            Line 3
            """
        )
        assert find_first_occurrence("hello world", source) is None
