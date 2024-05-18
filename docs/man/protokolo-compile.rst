..
  SPDX-FileCopyrightText: 2024 Carmen Bianca BAKKER <carmen@carmenbianca.eu>

  SPDX-License-Identifier: CC-BY-SA-4.0 OR GPL-3.0-or-later

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

A change log directory should contain a '.protokolo.toml' file that defines some
attributes of the section. This is an example file::

    [protokolo.section]
    title = "${version} - ${date}"
    level = 2

When the section is compiled, its heading may look like this::

    ## 1.0.0 - 2023-11-08

The heading is followed by the contents of files in the section's directory, and
subsections in subdirectories. If a section is empty (no change log fragments),
it is not compiled.

The change log file should contain the following comment, which is the location
in the file after which the compiled section will be pasted::

    <!-- protokolo-section-tag -->

For more documentation and options, read the documentation at
`<https://protokolo.readthedocs.io>`_.


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
