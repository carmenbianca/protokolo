..
  SPDX-FileCopyrightText: 2024 Carmen Bianca BAKKER <carmen@carmenbianca.eu>

  SPDX-License-Identifier: CC-BY-SA-4.0 OR GPL-3.0-or-later

protokolo-compile
=================

Synopsis
--------

**protokolo compile** [*--help*] [*options*]

Description
-----------

:program:`protokolo compile` aggregates the contents of a change log directory
into a new section in a change log file. The new section is inserted after the
first line in the change log containing the text ``protokolo-section-tag``.
Afterwards, the fragment files in the change log directory are deleted.

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
