# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the exception code."""

import pytest

from protokolo.exceptions import DictTypeError

# pylint: disable=pointless-exception-statement


class TestDictTypeError:
    """Collect all tests for DictTypeError."""

    def test_too_many_args(self):
        """Cannot create with too many args."""
        with pytest.raises(TypeError):
            DictTypeError(1, 2, 3, 4, 5)

    def test_no_args(self):
        """Can create with no args."""
        error = DictTypeError()
        assert error.key is None
        assert error.expected_type is None
        assert error.got is None
        assert error.source is None
        assert str(error) == ""

    def test_only_key(self):
        """Only key provided."""
        error = DictTypeError("title")
        assert error.key == "title"
        assert str(error) == "'title' does not have the correct type."

    def test_incl_expected_type(self):
        """Include up to expected_type."""
        error = DictTypeError("title", str)
        assert error.expected_type == str
        assert (
            str(error)
            == "'title' does not have the correct type. Expected str."
        )

    def test_expected_type_is_instance(self):
        """If the expected type is an instance of an object, still correctly
        print the __str__.
        """
        error = DictTypeError("title", "foo")
        assert error.expected_type == "foo"
        assert (
            str(error)
            == "'title' does not have the correct type. Expected str."
        )

    def test_incl_got(self):
        """Include up to got."""
        error = DictTypeError("title", str, 1)
        assert error.got == 1
        assert (
            str(error)
            == "'title' does not have the correct type. Expected str. Got 1."
        )

    def test_incl_source(self):
        """Include up to source."""
        error = DictTypeError("title", str, 1, "foo.toml")
        assert error.source == "foo.toml"
        assert (
            str(error)
            == "foo.toml: 'title' does not have the correct type. Expected str."
            " Got 1."
        )