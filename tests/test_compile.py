# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the compilation of change log sections and entries."""

import tomllib
from inspect import cleandoc
from io import BytesIO

import pytest

from protokolo.compile import Entry, Section, SectionAttributes


class TestSectionAttributes:
    """Collect all tests for SectionAttributes."""

    def test_level_positive(self):
        """level must be a positive integer."""
        SectionAttributes(level=1)
        with pytest.raises(ValueError):
            SectionAttributes(level=0)
        with pytest.raises(ValueError):
            SectionAttributes(level=-1)

    def test_order_positive(self):
        """order must be a positive integer."""
        SectionAttributes(order=1)
        SectionAttributes(order=None)
        with pytest.raises(ValueError):
            SectionAttributes(order=0)
        with pytest.raises(ValueError):
            SectionAttributes(order=-1)

    def test_from_dict_simple(self):
        """Provide all values."""
        values = {"title": "Title", "level": 2, "order": 3, "foo": "bar"}
        attrs = SectionAttributes.from_dict(values)
        assert attrs.title == "Title"
        assert attrs.level == 2
        assert attrs.order == 3
        assert attrs.other["foo"] == "bar"

    def test_from_dict_empty(self):
        """Initiating from an empty dictionary is the same as initiating an
        empty object.
        """
        from_dict = SectionAttributes.from_dict({})
        empty = SectionAttributes()
        assert (
            from_dict.title == empty.title == "TODO: No section title defined"
        )
        assert from_dict.level == empty.level == 1
        assert from_dict.order == empty.order == None
        # pylint: disable=use-implicit-booleaness-not-comparison
        assert from_dict.other == empty.other == {}

    def test_from_dict_wrong_type_level(self):
        """If the level is not an int, expect an error."""
        # No errors
        SectionAttributes.from_dict({"level": 1})
        SectionAttributes.from_dict({"level": None})
        # Errors
        wrong_values = {"1", 1.1, "1.1", "Foo", True}
        for value in wrong_values:
            with pytest.raises(ValueError):
                SectionAttributes.from_dict({"level": value})

    def test_from_dict_wrong_type_order(self):
        """If the order is not an int, expect an error."""
        # No errors
        SectionAttributes.from_dict({"order": 1})
        SectionAttributes.from_dict({"order": None})
        # Errors
        wrong_values = {"1", 1.1, "1.1", "Foo", True}
        for value in wrong_values:
            with pytest.raises(ValueError):
                SectionAttributes.from_dict({"order": value})

    def test_from_dict_wrong_type_title(self):
        """If the title is not a str, expect an error."""
        # No errors
        SectionAttributes.from_dict({"title": "Foo"})
        SectionAttributes.from_dict({"title": None})
        # Errors
        wrong_values = {1, 1.1, False}
        for value in wrong_values:
            with pytest.raises(ValueError):
                SectionAttributes.from_dict({"title": value})

    def test_from_dict_wrong_type_other(self):
        """If another value is not a str, expect an error."""
        # No errors
        SectionAttributes.from_dict({"foo": "bar"})
        SectionAttributes.from_dict({"title": None})
        # Errors
        wrong_values = {1, 1.1, False}
        for value in wrong_values:
            with pytest.raises(ValueError):
                SectionAttributes.from_dict({"foo": value})

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
        values = SectionAttributes.parse_toml(toml)
        assert values["title"] == "Title"
        assert values["level"] == 2
        assert values["order"] == 3
        assert values["foo"] == "bar"

    def test_parse_toml_no_values(self):
        """If there are no values, return an empty dictionary."""
        toml = cleandoc(
            """
            [protokolo.section]
            """
        )
        values = SectionAttributes.parse_toml(toml)
        assert not values

    def test_parse_toml_no_table(self):
        """If there is no [protokolo.section] table, expect a ValueError"""
        toml = cleandoc(
            """
            title = "Title"
            """
        )
        with pytest.raises(ValueError):
            SectionAttributes.parse_toml(toml)

    def test_parse_toml_decode_error(self):
        """Raise TOMLDecodeError when TOML can't be parsed."""
        yaml = cleandoc(
            """
            hello:
              - world
            """
        )
        with pytest.raises(tomllib.TOMLDecodeError):
            SectionAttributes.parse_toml(yaml)
        with BytesIO(yaml.encode("utf-8")) as fp:
            with pytest.raises(tomllib.TOMLDecodeError):
                SectionAttributes.parse_toml(fp)

    def test_from_toml_str_simple(self):
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
        attrs = SectionAttributes.from_toml(toml)
        assert attrs.title == "Title"
        assert attrs.level == 2
        assert attrs.order == 3
        assert attrs.other["foo"] == "bar"

    def test_from_toml_io_simple(self):
        """Provide all values in a toml IO."""
        toml = cleandoc(
            """
            [protokolo.section]
            title = "Title"
            level = 2
            order = 3
            foo = "bar"
            """
        ).encode("utf-8")
        toml_io = BytesIO(toml)
        attrs = SectionAttributes.from_toml(toml_io)
        assert attrs.title == "Title"
        assert attrs.level == 2
        assert attrs.order == 3
        assert attrs.other["foo"] == "bar"

    def test_from_toml_missing_table(self):
        """If the [protokolo.section] table is missing, expect a ValueError."""
        toml = cleandoc(
            """
            title = "Title"
            """
        )
        with pytest.raises(ValueError):
            SectionAttributes.from_toml(toml)


class TestSection:
    """Collect all tests for Section."""

    def test_compile_simple(self):
        """Test the compilation of a very simple section with one entry and one
        subsection.
        """
        subsection = Section(
            attrs=SectionAttributes(title="Subsection", level=2)
        )
        subsection.entries.add(Entry("- world"))
        section = Section(attrs=SectionAttributes(title="Section", level=1))
        section.entries.add(Entry("- hello"))
        section.subsections.add(subsection)

        expected = cleandoc(
            """
            # Section

            - hello

            ## Subsection

            - world
            """
        )
        assert section.compile() == expected

    def test_compile_empty(self):
        """Compile an empty section."""
        section = Section()
        assert section.compile() == "# TODO: No section title defined"

    def test_compile_order_specified(self):
        """Respect the order specified on the subsection."""
        subsection_1 = Section(
            attrs=SectionAttributes(title="Subsection Foo", level=2, order=1)
        )
        subsection_2 = Section(
            attrs=SectionAttributes(title="Subsection Bar", level=2, order=2)
        )
        section = Section(attrs=SectionAttributes(title="Section", level=1))
        section.subsections.add(subsection_1)
        section.subsections.add(subsection_2)

        expected = cleandoc(
            """
            # Section

            ## Subsection Foo

            ## Subsection Bar
            """
        )
        assert section.compile() == expected

    def test_compile_order_alphabetic(self):
        """If no orders are specified, sort subsections alphabetically."""
        subsection_1 = Section(
            attrs=SectionAttributes(title="Subsection Foo", level=2)
        )
        subsection_2 = Section(
            attrs=SectionAttributes(title="Subsection Bar", level=2)
        )
        section = Section(attrs=SectionAttributes(title="Section", level=1))
        section.subsections.add(subsection_1)
        section.subsections.add(subsection_2)

        expected = cleandoc(
            """
            # Section

            ## Subsection Bar

            ## Subsection Foo
            """
        )
        assert section.compile() == expected

    def test_compile_order_mixed(self):
        """Ordered subsections are sorted first, and all subsections with
        unspecified order are sorted afterwards, alphabetically.
        """
        subsection_1 = Section(
            attrs=SectionAttributes(title="Subsection Foo", level=2, order=1)
        )
        subsection_2 = Section(
            attrs=SectionAttributes(title="Subsection Bar", level=2, order=2)
        )
        subsection_3 = Section(
            attrs=SectionAttributes(title="Subsection Baz", level=2)
        )
        subsection_4 = Section(
            attrs=SectionAttributes(title="Subsection Quz", level=2)
        )
        section = Section(attrs=SectionAttributes(title="Section", level=1))
        section.subsections.update(
            {subsection_1, subsection_2, subsection_3, subsection_4}
        )
        expected = cleandoc(
            """
            # Section

            ## Subsection Foo

            ## Subsection Bar

            ## Subsection Baz

            ## Subsection Quz
            """
        )
        assert section.compile() == expected

    def test_compile_order_same_order(self):
        """If two sections have the same order number, sort alphabetically."""
        subsection_1 = Section(
            attrs=SectionAttributes(title="Subsection Foo", level=2, order=1)
        )
        subsection_2 = Section(
            attrs=SectionAttributes(title="Subsection Bar", level=2, order=1)
        )
        section = Section(attrs=SectionAttributes(title="Section", level=1))
        section.subsections.add(subsection_1)
        section.subsections.add(subsection_2)

        expected = cleandoc(
            """
            # Section

            ## Subsection Bar

            ## Subsection Foo
            """
        )
        assert section.compile() == expected

    def test_from_directory(self, project_dir):
        """A very simple case of generating a Section from a directory."""
        (project_dir / "changelog.d/announcement.md").write_text(
            "Hello, world!"
        )
        (project_dir / "changelog.d/feature/feature_1.md").write_text(
            "- Added feature."
        )
        section = Section.from_directory(project_dir / "changelog.d")
        assert section.attrs.level == 1
        assert section.attrs.title == "{version} - {date}"
        assert len(section.entries) == 1
        announcement = next(iter(section.entries))
        assert announcement.text == "Hello, world!"
        assert (
            announcement.source == project_dir / "changelog.d/announcement.md"
        )
        assert len(section.subsections) == 1
        subsection = next(iter(section.subsections))
        assert subsection.attrs.level == 2
        assert subsection.attrs.title == "Features"
        assert len(subsection.entries) == 1
        feature = next(iter(subsection.entries))
        assert feature.text == "- Added feature."
        assert (
            feature.source == project_dir / "changelog.d/feature/feature_1.md"
        )


class TestEntry:
    """Collect all tests for Entry."""

    def test_compile_simple(self):
        """Compile a simple entry."""
        entry = Entry("Hello, world!")
        assert entry.compile() == "Hello, world!"

    def test_compile_newlines(self):
        """Strip newlines from entry."""
        entry = Entry("\n\n\nFoo\n\n\n\n\n")
        assert entry.compile() == "Foo"
