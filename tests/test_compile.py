# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the compilation of change log sections and entries."""

from inspect import cleandoc

from protokolo.compile import Entry, Section, SectionAttributes


def test_simple_compile():
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
