..
  SPDX-FileCopyrightText: 2024 Carmen Bianca BAKKER <carmen@carmenbianca.eu>

  SPDX-License-Identifier: CC-BY-SA-4.0 OR EUPL-1.2+

protokolo-compile
=================

Synopsis
--------

**protokolo compile** [*options*]

Description
-----------

:program:`protokolo compile` aggregates the contents of a change log directory
into a new section in a change log file. Afterwards, the fragment files in the
change log directory are deleted.

The fragments are sorted alphabetically by file name stem, and section sorting
is described in :manpage:`protokolo(1)`.

A change log directory should contain a ``.protokolo.toml`` file that defines
some attributes of the section. This is an example file::

    [protokolo.section]
    title = "${version} - ${date}"
    level = 2

When the section is compiled, its heading may look like this::

    ## 1.0.0 - 2023-11-08

The heading is followed by the contents of files in the section's directory, and
subsections in subdirectories. If a section is empty (no change log fragments),
it is not compiled.

The section is inserted into the change log after the line containing the first
instance of ``protokolo-section-tag``. You typically want to comment that out.
The insertion always inserts two newlines at the start, effectively placing your
section two lines below ``protokolo-section-tag``. An example change log file is
as follows::

    # Change log

    Some text describing your change log.

    <!-- protokolo-section-tag -->

    ## 0.1.0 - 2023-10-25

    The latest release.

The compilation of the change log directory makes sure that after each section,
there are at least two newlines before the next section heading or fragment.
Before each subsection there are also at least two newlines after the preceding
section heading or fragment. These newlines can overlap, and are indicated below
using ``←``. Newlines that belong to fragments are indicated using ``↵``.

::

    # Top section←
    ←
    ## Subsection 1←
    ←
    - A fragment.↵
    - Another fragment.↵
    ←
    ## Subsection 2←
    ←
    - Last fragment.↵

Fragments are inserted as-is without any modification, except a newline is
appended at the end of a fragment if one was not present in the file.

Options with defaults
---------------------

If the below options are not defined, they default to the corresponding options
in the ``.protokolo.toml`` global configuration file if one exists, or otherwise
their base defaults if they have one.

.. option:: -c, --changelog

    **Required**. Path to the change log file into which to insert the compiled
    section.

.. option:: -d, --directory

    **Required**. Path to the change log directory to compile.

.. option:: -m, --markup

    Markup language to use. This determines how the headings are compiled and
    which files to search in the change log directory.

Other options
-------------

.. option:: -f, --format

    Repeatable. This option takes two parameters; a key and a value. Identically
    named placeholders in titles defined in ``.protokolo.toml`` section
    configuration files are substituted by the value.

.. option:: -n, --dry-run

    Do not write anything to the file system. Instead, print the resulting
    change log to *STDOUT*.

.. option:: --help

    Display help and exit.
