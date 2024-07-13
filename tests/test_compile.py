# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the compilation of change log sections and fragments."""

import random
import tomllib

import pytest

from protokolo._util import cleandoc_nl
from protokolo.compile import Fragment, Section
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
        """Test the compilation of a very simple section with one fragment and
        one subsection.
        """
        subsection = Section(
            attrs=SectionAttributes(title="Subsection", level=2)
        )
        subsection.fragments.add(Fragment("- world"))
        section = Section(attrs=SectionAttributes(title="Section", level=1))
        section.fragments.add(Fragment("- hello"))
        section.subsections.add(subsection)

        expected = cleandoc_nl(
            """
            # Section

            - hello

            ## Subsection

            - world
            """
        )
        assert section.compile() == expected

    def test_compile_multiple_fragments(self):
        """Test the compilation of a single section with multiple fragments.

        In this test, there are three types of newline configurations for
        fragments:

        - None
        - One newline
        - More newlines
        """
        section = Section(attrs=SectionAttributes(title="Section", level=1))
        section.fragments.add(Fragment("- A", source="a"))
        section.fragments.add(Fragment("- B\n", source="b"))
        section.fragments.add(Fragment("- C\n\n", source="c"))
        section.fragments.add(Fragment("- D", source="d"))
        section.fragments.add(Fragment("\n- E", source="e"))

        expected = cleandoc_nl(
            """
            # Section

            - A
            - B
            - C

            - D

            - E
            """
        )
        assert section.compile() == expected

    def test_compile_empty(self):
        """A section that contains neither fragments nor subsections doesn't
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
        subsection_1.fragments.add(Fragment("Foo"))
        subsection_2 = Section(
            attrs=SectionAttributes(title="Subsection Bar", level=2, order=2)
        )
        section = Section(attrs=SectionAttributes(title="Section", level=1))
        section.subsections.add(subsection_1)
        section.subsections.add(subsection_2)

        expected = cleandoc_nl(
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
        subsection_1.fragments.add(Fragment("Foo"))
        subsection_2 = Section(
            attrs=SectionAttributes(title="Subsection Bar", level=2, order=2)
        )
        subsection_2.fragments.add(Fragment("Bar"))
        section = Section(attrs=SectionAttributes(title="Section", level=1))
        section.subsections.add(subsection_1)
        section.subsections.add(subsection_2)

        expected = cleandoc_nl(
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
        subsection_1.fragments.add(Fragment("Foo"))
        subsection_2 = Section(
            attrs=SectionAttributes(title="Subsection Bar", level=2)
        )
        subsection_2.fragments.add(Fragment("Bar"))
        section = Section(attrs=SectionAttributes(title="Section", level=1))
        section.subsections.add(subsection_1)
        section.subsections.add(subsection_2)

        expected = cleandoc_nl(
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
        subsection_1.fragments.add(Fragment("Foo"))
        subsection_2 = Section(
            attrs=SectionAttributes(title="Subsection Bar", level=2, order=2)
        )
        subsection_2.fragments.add(Fragment("Bar"))
        subsection_3 = Section(
            attrs=SectionAttributes(title="Subsection Baz", level=2)
        )
        subsection_3.fragments.add(Fragment("Baz"))
        subsection_4 = Section(
            attrs=SectionAttributes(title="Subsection Quz", level=2)
        )
        subsection_4.fragments.add(Fragment("Quz"))
        section = Section(attrs=SectionAttributes(title="Section", level=1))
        section.subsections.update(
            {subsection_1, subsection_2, subsection_3, subsection_4}
        )
        expected = cleandoc_nl(
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
        subsection_1.fragments.add(Fragment("Foo"))
        subsection_2 = Section(
            attrs=SectionAttributes(title="Subsection Bar", level=2, order=1)
        )
        subsection_2.fragments.add(Fragment("Bar"))
        section = Section(attrs=SectionAttributes(title="Section", level=1))
        section.subsections.add(subsection_1)
        section.subsections.add(subsection_2)

        expected = cleandoc_nl(
            """
            # Section

            ## Subsection Bar

            Bar

            ## Subsection Foo

            Foo
            """
        )
        assert section.compile() == expected

    def test_compile_fragments_sorted_by_source(self):
        """Compiled fragments are sorted by their source."""
        section = Section(attrs=SectionAttributes(title="Section"))
        fragments = {
            f"{source_nr}.md": str(random.randint(1, 10_000))
            for source_nr in range(10)
        }
        for source, text in fragments.items():
            section.fragments.add(Fragment(text, source=source))

        expected = (
            "# Section\n\n"
            + "\n".join(item[1] for item in sorted(fragments.items()))
            + "\n"
        )
        assert section.compile() == expected

    def test_compile_fragments_sorted_by_source_stem(self):
        """foo-bar.md is sorted after foo.md."""
        section = Section(attrs=SectionAttributes(title="Section"))
        for item in ["foo-bar.md", "foo.md"]:
            section.fragments.add(Fragment(item, source=item))

        expected = cleandoc_nl(
            """
            # Section

            foo.md
            foo-bar.md
            """
        )
        assert section.compile() == expected

    def test_compile_fragments_sorted_by_text(self):
        """Compiled fragments are sorted alphabetically by their text if they
        have no source.
        """
        section = Section(attrs=SectionAttributes(title="Section"))
        fragments = {str(random.randint(1, 10_000)) for _ in range(10)}
        for text in fragments:
            section.fragments.add(Fragment(text))

        expected = "# Section\n\n" + "\n".join(sorted(fragments)) + "\n"
        assert section.compile() == expected

    def test_compile_fragments_sorted_mixed(self):
        """Compiled fragments that have a source are sorted before ones that
        don't.
        """
        section = Section(attrs=SectionAttributes(title="Section"))
        section.fragments.add(Fragment("- Foo", source="foo.md"))
        section.fragments.add(Fragment("- Bar"))

        expected = cleandoc_nl(
            """
            # Section

            - Foo
            - Bar
            """
        )
        assert section.compile() == expected

    def test_is_empty_simple(self):
        """A section with neither fragments nor subsections is empty."""
        section = Section()
        assert section.is_empty()

    def test_is_empty_contains_fragments(self):
        """A section with fragments is not empty."""
        section = Section()
        section.fragments.add(Fragment("Foo"))
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
        subsection.fragments.add(Fragment("Hello"))
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
        assert len(section.fragments) == 1
        announcement = next(iter(section.fragments))
        assert announcement.text == "Hello, world!"
        assert (
            announcement.source == project_dir / "changelog.d/announcement.md"
        )
        assert len(section.subsections) == 1
        subsection = next(iter(section.subsections))
        assert subsection.attrs.level == 3
        assert subsection.attrs.title == "Features"
        assert len(subsection.fragments) == 1
        feature = next(iter(subsection.fragments))
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
            cleandoc_nl(
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
            cleandoc_nl(
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

    def test_from_directory_no_protokolo_toml_in_subdir(self, project_dir):
        """If there is no .protokolo.toml in the subdirectory, don't count it as
        a section.
        """
        (project_dir / "changelog.d/feature/.protokolo.toml").unlink()
        section = Section.from_directory(project_dir / "changelog.d")
        assert not section.subsections

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


class TestFragment:
    """Collect all tests for Fragment."""

    def test_compile_simple(self):
        """Compile a simple fragment."""
        fragment = Fragment("Hello, world!\n")
        assert fragment.compile() == "Hello, world!\n"

    def test_compile_no_newline_at_end(self):
        """Add missing newline to fragment."""
        fragment = Fragment("Foo")
        assert fragment.compile() == "Foo\n"
