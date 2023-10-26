# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the compilation of change log sections and entries."""

import random
import tomllib
from inspect import cleandoc
from io import BytesIO

import pytest

from protokolo.compile import Entry, Section, SectionAttributes
from protokolo.exceptions import AttributeNotPositiveError, DictTypeError


class TestSectionAttributes:
    """Collect all tests for SectionAttributes."""

    def test_level_positive(self):
        """level must be a positive integer."""
        SectionAttributes(level=1)
        # Automagically fix unexpected type
        attrs = SectionAttributes(level=None)  # type: ignore
        assert attrs.level == 1
        with pytest.raises(AttributeNotPositiveError):
            SectionAttributes(level=0)
        with pytest.raises(AttributeNotPositiveError):
            SectionAttributes(level=-1)

    def test_order_positive(self):
        """order must be a positive integer."""
        SectionAttributes(order=1)
        SectionAttributes(order=None)
        with pytest.raises(AttributeNotPositiveError):
            SectionAttributes(order=0)
        with pytest.raises(AttributeNotPositiveError):
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
        SectionAttributes.from_dict({"order": None})
        # Errors
        wrong_values = {"1", 1.1, "1.1", "Foo", True}
        for value in wrong_values:
            with pytest.raises(DictTypeError) as exc_info:
                SectionAttributes.from_dict({"order": value})
            error = exc_info.value
            assert error.key == "order"
            assert error.expected_type == int
            assert error.got == value

    def test_from_dict_wrong_type_title(self):
        """If the title is not a str, expect an error."""
        # No errors
        SectionAttributes.from_dict({"title": "Foo"})
        SectionAttributes.from_dict({"title": None})
        # Errors
        wrong_values = {1, 1.1, False}
        for value in wrong_values:
            with pytest.raises(DictTypeError) as exc_info:
                SectionAttributes.from_dict({"title": value})
            error = exc_info.value
            assert error.key == "title"
            assert error.expected_type == str
            assert error.got == value

    def test_from_dict_wrong_type_other(self):
        """If another value is not a str, expect an error."""
        # No errors
        SectionAttributes.from_dict({"foo": "bar"})
        SectionAttributes.from_dict({"title": None})
        # Errors
        wrong_values = {1, 1.1, False}
        for value in wrong_values:
            with pytest.raises(DictTypeError) as exc_info:
                SectionAttributes.from_dict({"foo": value})
            error = exc_info.value
            assert error.key == "foo"
            assert error.expected_type == str
            assert error.got == value

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
        """If there is no [protokolo.section] table, return an empty dict."""
        toml = cleandoc(
            """
            title = "Title"
            """
        )
        assert SectionAttributes.parse_toml(toml) == {}

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

    def test_parse_toml_wrong_type(self):
        """Passing the wrong type results in an error."""
        values = {"title": "Section"}
        with pytest.raises(TypeError):
            SectionAttributes.parse_toml(values)  # type: ignore

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
        """If the [protokolo.section] table is missing, return an empty
        SectionAttributes.
        """
        toml = cleandoc(
            """
            title = "Title"
            """
        )
        result = SectionAttributes.from_toml(toml)
        assert result.title == "TODO: No section title defined"


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
        """A section that contains neither entries nor subsections doesn't
        compile to anything.
        """
        section = Section()
        assert section.compile() == ""

    def test_compile_empty_subsections(self):
        """A section that only contains empty subsections doesn't compile to
        anything.
        """
        subsection = Section()
        section = Section()
        section.subsections.add(subsection)
        assert section.compile() == ""

    def test_compile_one_empty_subsection(self):
        """If one subsection is empty, and the other is not, the empty
        subsection should not be compiled.
        """
        subsection_1 = Section(
            attrs=SectionAttributes(title="Subsection Foo", level=2, order=1)
        )
        subsection_1.entries.add(Entry("Foo"))
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

            Foo
            """
        )
        assert section.compile() == expected

    def test_compile_order_specified(self):
        """Respect the order specified on the subsection."""
        subsection_1 = Section(
            attrs=SectionAttributes(title="Subsection Foo", level=2, order=1)
        )
        subsection_1.entries.add(Entry("Foo"))
        subsection_2 = Section(
            attrs=SectionAttributes(title="Subsection Bar", level=2, order=2)
        )
        subsection_2.entries.add(Entry("Bar"))
        section = Section(attrs=SectionAttributes(title="Section", level=1))
        section.subsections.add(subsection_1)
        section.subsections.add(subsection_2)

        expected = cleandoc(
            """
            # Section

            ## Subsection Foo

            Foo

            ## Subsection Bar

            Bar
            """
        )
        assert section.compile() == expected

    def test_compile_order_alphabetic(self):
        """If no orders are specified, sort subsections alphabetically."""
        subsection_1 = Section(
            attrs=SectionAttributes(title="Subsection Foo", level=2)
        )
        subsection_1.entries.add(Entry("Foo"))
        subsection_2 = Section(
            attrs=SectionAttributes(title="Subsection Bar", level=2)
        )
        subsection_2.entries.add(Entry("Bar"))
        section = Section(attrs=SectionAttributes(title="Section", level=1))
        section.subsections.add(subsection_1)
        section.subsections.add(subsection_2)

        expected = cleandoc(
            """
            # Section

            ## Subsection Bar

            Bar

            ## Subsection Foo

            Foo
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
        subsection_1.entries.add(Entry("Foo"))
        subsection_2 = Section(
            attrs=SectionAttributes(title="Subsection Bar", level=2, order=2)
        )
        subsection_2.entries.add(Entry("Bar"))
        subsection_3 = Section(
            attrs=SectionAttributes(title="Subsection Baz", level=2)
        )
        subsection_3.entries.add(Entry("Baz"))
        subsection_4 = Section(
            attrs=SectionAttributes(title="Subsection Quz", level=2)
        )
        subsection_4.entries.add(Entry("Quz"))
        section = Section(attrs=SectionAttributes(title="Section", level=1))
        section.subsections.update(
            {subsection_1, subsection_2, subsection_3, subsection_4}
        )
        expected = cleandoc(
            """
            # Section

            ## Subsection Foo

            Foo

            ## Subsection Bar

            Bar

            ## Subsection Baz

            Baz

            ## Subsection Quz

            Quz
            """
        )
        assert section.compile() == expected

    def test_compile_order_same_order(self):
        """If two sections have the same order number, sort alphabetically."""
        subsection_1 = Section(
            attrs=SectionAttributes(title="Subsection Foo", level=2, order=1)
        )
        subsection_1.entries.add(Entry("Foo"))
        subsection_2 = Section(
            attrs=SectionAttributes(title="Subsection Bar", level=2, order=1)
        )
        subsection_2.entries.add(Entry("Bar"))
        section = Section(attrs=SectionAttributes(title="Section", level=1))
        section.subsections.add(subsection_1)
        section.subsections.add(subsection_2)

        expected = cleandoc(
            """
            # Section

            ## Subsection Bar

            Bar

            ## Subsection Foo

            Foo
            """
        )
        assert section.compile() == expected

    def test_compile_entries_sorted_by_source(self):
        """Compiled entries are sorted by their source."""
        section = Section(attrs=SectionAttributes(title="Section"))
        entries = {
            f"{source_nr}.md": str(random.randint(1, 10_000))
            for source_nr in range(10)
        }
        for source, text in entries.items():
            section.entries.add(Entry(text, source=source))

        expected = "# Section\n\n" + "\n\n".join(
            item[1] for item in sorted(entries.items())
        )
        assert section.compile() == expected

    def test_compile_entries_sorted_by_text(self):
        """Compiled entries are sorted alphabetically by their text if they have
        no source.
        """
        section = Section(attrs=SectionAttributes(title="Section"))
        entries = {str(random.randint(1, 10_000)) for _ in range(10)}
        for text in entries:
            section.entries.add(Entry(text))

        expected = "# Section\n\n" + "\n\n".join(sorted(entries))
        assert section.compile() == expected

    def test_compile_entries_sorted_mixed(self):
        """Compiled entries that have a source are sorted before ones that
        don't.
        """
        section = Section(attrs=SectionAttributes(title="Section"))
        section.entries.add(Entry("Foo", source="foo.md"))
        section.entries.add(Entry("Bar"))

        expected = cleandoc(
            """
            # Section

            Foo

            Bar
            """
        )
        assert section.compile() == expected

    def test_is_empty_simple(self):
        """A section with neither entries nor subsections is empty."""
        section = Section()
        assert section.is_empty()

    def test_is_empty_contains_entries(self):
        """A section with entries is not empty."""
        section = Section()
        section.entries.add(Entry("Foo"))
        assert not section.is_empty()

    def test_is_empty_with_empty_subsections(self):
        """A section with empty subsections is empty."""
        subsection = Section()
        section = Section()
        section.subsections.add(subsection)
        assert subsection.is_empty()
        assert section.is_empty()

    def test_is_empty_with_nonempty_subsections(self):
        """A section with non-empty subsections is not empty."""
        subsection = Section()
        subsection.entries.add(Entry("Hello"))
        section = Section()
        section.subsections.add(subsection)
        assert not subsection.is_empty()
        assert not section.is_empty()

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

    def test_from_directory_decode_error(self, project_dir):
        """Raise TOMLDecodeError if there is invalid TOML."""
        (project_dir / "changelog.d/.protokolo.toml").write_text(
            "{'hello': 'world'}"
        )
        with pytest.raises(tomllib.TOMLDecodeError) as exc_info:
            Section.from_directory(project_dir / "changelog.d")
        error = exc_info.value
        assert (
            f"Invalid TOML in '{project_dir / 'changelog.d/.protokolo.toml'}'"
            in str(error)
        )

    def test_from_directory_dict_type_error(self, project_dir):
        """If there is a type inconsistency is found in the toml file, raise a
        DictTypeError.
        """
        (project_dir / "changelog.d/.protokolo.toml").write_text(
            cleandoc(
                """
                [protokolo.section]
                level = "foo"
                """
            )
        )
        with pytest.raises(DictTypeError) as exc_info:
            Section.from_directory(project_dir / "changelog.d")
        error = exc_info.value
        assert error.source == str(project_dir / "changelog.d/.protokolo.toml")

    def test_from_directory_attribute_not_positive_error(self, project_dir):
        """If a value in .protokolo.toml must be positive but isn't, raise
        AttributeNotPositiveError.
        """
        (project_dir / "changelog.d/.protokolo.toml").write_text(
            cleandoc(
                """
                [protokolo.section]
                level = 0
                """
            )
        )
        with pytest.raises(AttributeNotPositiveError) as exc_info:
            Section.from_directory(project_dir / "changelog.d")
        error = exc_info.value
        assert (
            f"Wrong value in '{project_dir / 'changelog.d/.protokolo.toml'}'"
        ) in str(error)


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