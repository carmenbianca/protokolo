# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the config code."""

import tomllib
from datetime import date, datetime
from inspect import cleandoc
from io import BytesIO

import pytest

from protokolo.config import (
    GlobalConfig,
    SectionAttributes,
    TOMLConfig,
    parse_toml,
)
from protokolo.exceptions import (
    AttributeNotPositiveError,
    DictTypeError,
    DictTypeListError,
)
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
            "list-primitive": [1, 2],
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
        assert config["list-primitive"] == [1, 2]

    def test_from_dict_unsupported_type(self):
        """Many complex types are not supported."""
        value = object()
        with pytest.raises(DictTypeError) as exc_info:
            TOMLConfig.from_dict({"foo": value})
        error = exc_info.value
        assert error.key == "foo"
        assert error.expected_type == TOMLValueType
        # TODO: This is not true because error.got is a (deep)copy of value.
        # assert error.got == value

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

    def test_validate_list_item(self):
        """List items get a special exception DictTypeListError."""
        config = TOMLConfig()
        value = object()
        config["foo"] = [value]  # type: ignore
        with pytest.raises(DictTypeListError) as exc_info:
            config.validate()
        error = exc_info.value
        assert error.key == "foo"
        assert error.expected_type == TOMLValueType
        assert error.got == value


class TestSectionAttributes:
    """Collect all tests for SectionAttributes."""

    def test_level_positive(self):
        """level must be a positive integer."""
        SectionAttributes(level=1)
        with pytest.raises(AttributeNotPositiveError):
            SectionAttributes(level=0)
        with pytest.raises(AttributeNotPositiveError):
            SectionAttributes(level=-1)

    def test_order_positive(self):
        """order must be a positive integer."""
        SectionAttributes(order=1)
        with pytest.raises(AttributeNotPositiveError):
            SectionAttributes(order=0)
        with pytest.raises(AttributeNotPositiveError):
            SectionAttributes(order=-1)

    def test_from_dict_simple(self):
        """Provide all values."""
        values = {"title": "Title", "level": 2, "order": 3, "foo": "bar"}
        attrs = SectionAttributes.from_dict(values)
        # https://github.com/pylint-dev/pylint/issues/9203
        # pylint: disable=no-member
        assert attrs.title == "Title"
        assert attrs.level == 2
        assert attrs.order == 3
        assert attrs["foo"] == "bar"

    def test_from_dict_empty(self):
        """Initiating from an empty dictionary is the same as initiating an
        empty object.
        """
        from_dict = SectionAttributes.from_dict({})
        empty = SectionAttributes()
        # https://github.com/pylint-dev/pylint/issues/9203
        # pylint: disable=no-member
        assert (
            from_dict.title == empty.title == "TODO: No section title defined"
        )
        assert from_dict.level == empty.level == 1
        assert from_dict.order == empty.order == None

    def test_from_dict_wrong_type_level(self):
        """If the level is not an int, expect an error."""
        # No errors
        SectionAttributes.from_dict({"level": 1})
        # Errors
        wrong_values = {"1", 1.1, "1.1", "Foo", True}
        for value in wrong_values:
            with pytest.raises(DictTypeError) as exc_info:
                SectionAttributes.from_dict({"level": value})
            error = exc_info.value
            assert error.key == "level"
            assert error.expected_type == int
            assert error.got == value

    def test_from_dict_wrong_type_order(self):
        """If the order is not an int, expect an error."""
        # No errors
        SectionAttributes.from_dict({"order": 1})
        # Errors
        wrong_values = {"1", 1.1, "1.1", "Foo", True}
        for value in wrong_values:
            with pytest.raises(DictTypeError) as exc_info:
                SectionAttributes.from_dict({"order": value})
            error = exc_info.value
            assert error.key == "order"
            assert error.expected_type == int | None
            assert error.got == value

    def test_from_dict_wrong_type_title(self):
        """If the title is not a str, expect an error."""
        # No errors
        SectionAttributes.from_dict({"title": "Foo"})
        # Errors
        wrong_values = {1, 1.1, False}
        for value in wrong_values:
            with pytest.raises(DictTypeError) as exc_info:
                SectionAttributes.from_dict({"title": value})
            error = exc_info.value
            assert error.key == "title"
            assert error.expected_type == str
            assert error.got == value

    def test_from_dict_subdict(self):
        """Don't raise an error if there is a subdict."""
        attrs = SectionAttributes.from_dict({"foo": {"bar": "quz"}})
        assert attrs["foo"] == {"bar": "quz"}


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

    def test_find_config_is_dir(self, project_dir):
        """Return None if config file is a directory."""
        (project_dir / ".protokolo.toml").mkdir()
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
