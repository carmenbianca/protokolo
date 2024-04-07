# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the compilation of change log sections and entries."""

import random
import tomllib
from inspect import cleandoc

import pytest

from protokolo.compile import Entry, Section
from protokolo.config import SectionAttributes
from protokolo.exceptions import (
    AttributeNotPositiveError,
    DictTypeError,
    ProtokoloTOMLIsADirectoryError,
    ProtokoloTOMLNotFoundError,
)

# pylint: disable=too-many-public-methods


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
        assert section.attrs.level == 2
        assert (
            # Strange pylint false positive here.
            section.attrs.title  # pylint: disable=no-member
            == "${version} - ${date}"
        )
        assert len(section.entries) == 1
        announcement = next(iter(section.entries))
        assert announcement.text == "Hello, world!"
        assert (
            announcement.source == project_dir / "changelog.d/announcement.md"
        )
        assert len(section.subsections) == 1
        subsection = next(iter(section.subsections))
        assert subsection.attrs.level == 3
        assert subsection.attrs.title == "Features"
        assert len(subsection.entries) == 1
        feature = next(iter(subsection.entries))
        assert feature.text == "- Added feature."
        assert (
            feature.source == project_dir / "changelog.d/feature/feature_1.md"
        )

    def test_from_directory_additional_format_pairs(self, project_dir):
        """Provide additional section format pairs to Section, and make sure
        they are set on the SectionAttributes.
        """
        section = Section.from_directory(
            project_dir / "changelog.d",
            section_format_pairs={"version": "0.2.0"},
        )
        assert section.attrs["version"] == "0.2.0"
        for subsection in section.subsections:
            assert subsection.attrs["version"] == "0.2.0"

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

    def test_from_directory_not_found_error(self, project_dir):
        """If .protokolo.toml does not exist, raise a
        ProtokoloTOMLNotFoundError.
        """
        (project_dir / "changelog.d/.protokolo.toml").unlink()
        with pytest.raises(ProtokoloTOMLNotFoundError) as exc_info:
            Section.from_directory(project_dir / "changelog.d")
        error = exc_info.value
        assert error.filename == str(
            project_dir / "changelog.d/.protokolo.toml"
        )

    def test_from_directory_is_a_directory_error(self, project_dir):
        """If .protokolo.toml is not a file, raise
        ProtokoloTOMLIsADirectoryError.
        """
        (project_dir / "changelog.d/.protokolo.toml").unlink()
        (project_dir / "changelog.d/.protokolo.toml").mkdir()
        with pytest.raises(ProtokoloTOMLIsADirectoryError) as exc_info:
            Section.from_directory(project_dir / "changelog.d")
        error = exc_info.value
        assert error.filename == str(
            project_dir / "changelog.d/.protokolo.toml"
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
