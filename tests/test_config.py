# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the config code."""

import tomllib
from datetime import date, datetime
from inspect import cleandoc
from io import BytesIO

import pytest

from protokolo.config import TOMLConfig, parse_toml
from protokolo.exceptions import DictTypeError, DictTypeListError
from protokolo.types import TOMLValueType


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


class TestTOMLConfig:
    """Collect all tests for TOMLConfig."""

    def test_from_dict_simple(self):
        """Given a simple dictionary, create a Config."""
        now_datetime = datetime.now()
        now_date = date.today()
        values = {
            "str": "foo",
            "int": 100,
            "float": 3.14,
            "bool": True,
            "datetime": now_datetime,
            "date": now_date,
            "none": None,
            "dict": {"foo": "bar"},
            "list": [{"foo": "bar"}, {"baz": "quz"}],
        }
        config = TOMLConfig.from_dict(values)
        assert config["str"] == "foo"
        assert config["int"] == 100
        assert config["float"] == 3.14
        assert config["bool"] is True
        assert config["datetime"] == now_datetime
        assert config["date"] == now_date
        assert config["none"] is None
        assert config["dict"] == {"foo": "bar"}
        assert config["list"] == [{"foo": "bar"}, {"baz": "quz"}]

    def test_from_dict_unsupported_type(self):
        """Many complex types are not supported."""
        value = object()
        with pytest.raises(DictTypeError) as exc_info:
            TOMLConfig.from_dict({"foo": value})
        error = exc_info.value
        assert error.key == "foo"
        assert error.expected_type == TOMLValueType
        assert error.got == value

    def test_from_dict_list_no_dict_inside(self):
        """A list is always a list of dicts."""
        with pytest.raises(DictTypeListError) as exc_info:
            TOMLConfig.from_dict({"foo": [1]})
        error = exc_info.value
        assert error.key == "foo"
        assert error.expected_type == dict
        assert error.got == 1

    def test_setitem(self):
        """You can set an item on the TOMLConfig object."""
        config = TOMLConfig.from_dict({"foo": "bar"})
        config["foo"] = "baz"
        assert config["foo"] == "baz"

    def test_setitem_doesnt_exist(self):
        """You are able to set an item that does not yet exist on the TOMLConfig
        object.
        """
        config = TOMLConfig()
        config["foo"] = "bar"
        assert config["foo"] == "bar"

    def test_setitem_nested(self):
        """You can set an item in a nested dictionary/table."""
        config = TOMLConfig.from_dict({"foo": {}})
        config[("foo", "bar")] = "baz"
        assert config[("foo", "bar")] == "baz"
        assert config["foo"] == {"bar": "baz"}

    def test_validate_simple(self):
        """Validate correctly identifies wrong types."""
        config = TOMLConfig()
        value = object()
        config["foo"] = value  # type: ignore
        with pytest.raises(DictTypeError) as exc_info:
            config.validate()
        error = exc_info.value
        assert error.key == "foo"
        assert error.expected_type == TOMLValueType
        assert error.got == value
