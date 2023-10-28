# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the config code."""

import tomllib
from datetime import date, datetime
from inspect import cleandoc
from io import BytesIO

import pytest

from protokolo.config import GlobalConfig, TOMLConfig, parse_toml
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
        values = parse_toml(toml, section=["protokolo", "section"])
        assert values["title"] == "Title"
        assert values["level"] == 2
        assert values["order"] == 3
        assert values["foo"] == "bar"
        parent = parse_toml(toml, section=["protokolo"])
        assert parent["section"] == values

    def test_parse_toml_no_values(self):
        """If there are no values, return an empty dictionary."""
        toml = cleandoc(
            """
            [protokolo.section]
            """
        )
        values = parse_toml(toml, section=["protokolo", "section"])
        assert not values

    def test_parse_toml_no_table(self):
        """If there is no [protokolo.section] table, return an empty dict."""
        toml = cleandoc(
            """
            title = "Title"
            """
        )
        assert parse_toml(toml, section=["protokolo"]) == {}
        assert parse_toml(toml, section=None) == {"title": "Title"}

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

    def test_validate_simple_expected(self):
        """No error when validating a valid expected type."""
        config = TOMLConfig.from_dict({"foo": "bar"})
        config.expected_types = {"foo": str}
        config.validate()

    def test_validate_nested_expected(self):
        """No error when validating a valid nested expected type."""
        config = TOMLConfig.from_dict({"foo": {"bar": "baz"}})
        config.expected_types = {"foo": dict, "foo+dict": {"bar": str}}
        config.validate()

    def test_validate_simple_not_expected(self):
        """Error when validating an invalid expected type."""
        config = TOMLConfig.from_dict({"foo": "bar"})
        config.expected_types = {"foo": int}
        with pytest.raises(DictTypeError) as exc_info:
            config.validate()
        error = exc_info.value
        assert error.key == "foo"
        assert error.expected_type == int
        assert error.got == "bar"

    def test_validate_list_wrong_type(self):
        """If a value is a list instead of the expected type, raise an error."""
        config = TOMLConfig.from_dict({"foo": [{"bar": "baz"}]})
        config.expected_types = {"foo": str}
        with pytest.raises(DictTypeError) as exc_info:
            config.validate()
        error = exc_info.value
        assert error.key == "foo"
        assert error.expected_type == str
        assert error.got == [{"bar": "baz"}]

    def test_validate_dict_wrong_type(self):
        """If a value is a dict instead of the expected type, raise an error."""
        config = TOMLConfig.from_dict({"foo": {"bar": "baz"}})
        config.expected_types = {"foo": str}
        with pytest.raises(DictTypeError) as exc_info:
            config.validate()
        error = exc_info.value
        assert error.key == "foo"
        assert error.expected_type == str
        assert error.got == {"bar": "baz"}

    def test_validate_item_of_list(self):
        """Validate the items of lists."""
        config = TOMLConfig.from_dict({"foo": [{"bar": "baz"}, {"bar": "quz"}]})
        config.expected_types = {"foo": list, "foo+list": {"bar": str}}
        config.validate()

    def test_validate_very_nested(self):
        """A rather complex nesting test."""
        config = TOMLConfig.from_dict(
            {
                "foo": {
                    "bar": {
                        "baz": [
                            {"quz": 1},
                            {"quz": 2},
                        ]
                    }
                }
            }
        )
        config.expected_types = {
            "foo": dict,
            "foo+dict": {
                "bar": dict,
                "bar+dict": {
                    "baz": list,
                    "baz+list": {
                        "quz": int,
                    },
                },
            },
        }
        config.validate()


class TestGlobalConfig:
    """Collect all tests for GlobalConfig."""

    def test_find_config_protokolo_toml(self, project_dir):
        """Find config at .protokolo.toml"""
        (project_dir / ".protokolo.toml").touch()
        assert GlobalConfig.find_config(project_dir) == (
            project_dir / ".protokolo.toml"
        )

    def test_find_config_pyproject_toml(self, project_dir):
        """Find config at pyproject.toml"""
        (project_dir / "pyproject.toml").touch()
        assert GlobalConfig.find_config(project_dir) == (
            project_dir / "pyproject.toml"
        )

    def test_find_config_none(self, project_dir):
        """Don't find any config."""
        assert GlobalConfig.find_config(project_dir) is None

    def test_from_file_protokolo_toml(self, project_dir):
        """Load from .protokolo.toml."""
        (project_dir / ".protokolo.toml").write_text(
            cleandoc(
                """
                [protokolo]
                changelog = "CHANGELOG"
                markup = "markdown"
                directory = "changelog.d"
                """
            )
        )
        config = GlobalConfig.from_file(project_dir / ".protokolo.toml")
        assert config.changelog == "CHANGELOG"
        assert config.markup == "markdown"
        assert config.directory == "changelog.d"

    def test_from_file_pyproject_toml(self, project_dir):
        """Load from pyproject.toml."""
        (project_dir / "pyproject.toml").write_text(
            cleandoc(
                """
                [tool.protokolo]
                changelog = "CHANGELOG"
                markup = "markdown"
                directory = "changelog.d"
                """
            )
        )
        config = GlobalConfig.from_file(project_dir / "pyproject.toml")
        assert config.changelog == "CHANGELOG"
        assert config.markup == "markdown"
        assert config.directory == "changelog.d"
