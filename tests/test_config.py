# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the config code."""

import tomllib
from inspect import cleandoc
from io import BytesIO

import pytest

from protokolo.config import parse_toml


class TestParseToml:
    """Collect all tests for parse_toml."""

    def test_parse_toml_simple(self):
        """Provide all values in a toml string."""
        toml = cleandoc(
            """
            [protokolo.section]
            title = "Title"
            level = 2
            order = 3
            foo = "bar"
            """
        )
        values = parse_toml(toml, sections=["protokolo", "section"])
        assert values["title"] == "Title"
        assert values["level"] == 2
        assert values["order"] == 3
        assert values["foo"] == "bar"
        parent = parse_toml(toml, sections=["protokolo"])
        assert parent["section"] == values

    def test_parse_toml_no_values(self):
        """If there are no values, return an empty dictionary."""
        toml = cleandoc(
            """
            [protokolo.section]
            """
        )
        values = parse_toml(toml, sections=["protokolo", "section"])
        assert not values

    def test_parse_toml_no_table(self):
        """If there is no [protokolo.section] table, return an empty dict."""
        toml = cleandoc(
            """
            title = "Title"
            """
        )
        assert parse_toml(toml, sections=["protokolo"]) == {}
        assert parse_toml(toml, sections=None) == {"title": "Title"}

    def test_parse_toml_decode_error(self):
        """Raise TOMLDecodeError when TOML can't be parsed."""
        yaml = cleandoc(
            """
            hello:
              - world
            """
        )
        with pytest.raises(tomllib.TOMLDecodeError):
            parse_toml(yaml)
        with BytesIO(yaml.encode("utf-8")) as fp:
            with pytest.raises(tomllib.TOMLDecodeError):
                parse_toml(fp)

    def test_parse_toml_wrong_type(self):
        """Passing the wrong type results in an error."""
        values = {"title": "Section"}
        with pytest.raises(TypeError):
            parse_toml(values)  # type: ignore
