# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the compilation of change log sections and entries."""

from inspect import cleandoc

from protokolo.compile import Entry, Section, SectionAttributes


def test_section_compile_simple():
    """Test the compilation of a very simple section with one entry and one
    subsection.
    """
    subsection = Section(attrs=SectionAttributes(title="Subsection", level=2))
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


def test_section_compile_empty():
    """Compile an empty section."""
    section = Section()
    assert section.compile() == "# TODO: No section title defined"


def test_section_compile_order_specified():
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


def test_section_compile_order_alphabetic():
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


def test_section_compile_order_mixed():
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


def test_section_compile_order_same_order():
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


def test_entry_compile_simple():
    """Compile a simple entry."""
    entry = Entry("Hello, world!")
    assert entry.compile() == "Hello, world!"


def test_entry_compile_newlines():
    """Strip newlines from entry."""
    entry = Entry("\n\n\nFoo\n\n\n\n\n")
    assert entry.compile() == "Foo"
