..
  SPDX-FileCopyrightText: 2024 Carmen Bianca BAKKER <carmen@carmenbianca.eu>

  SPDX-License-Identifier: CC-BY-SA-4.0 OR EUPL-1.2+

protokolo
=========

Synopsis
--------

**protokolo** [*options*] <command>

Description
-----------

:program:`protokolo` allows you to maintain your change log fragments in
separate files, and then finally aggregate them into a new section in CHANGELOG
just before release.

The change log directory, typically named ``changelog.d`` in the root of your
project, is a hierarchy of files (fragments) and directories (sections) that can
be compiled into a change log file. The top section---the change log directory
itself---typically maps to the section of a version release in your change log
file.

The change log directory and all its subdirectories must contain a
``.protokolo.toml`` :ref:`section configuration <section-configuration>` file.
If a directory does not contain such a file, it is not a section, and is
consequently ignored.

The :ref:`fragments <fragments>` must have a file extension corresponding to
their markup language. If a file does not have such a file extension, it is not
a fragment, and is consequently ignored by Protokolo.

As an example, the change log directory typically looks like this:

::

   .
   └── changelog.d
       ├── added
       │   ├── new-feature.md
       │   └── .protokolo.toml
       ├── fixed
       │   ├── fix-lag.md
       │   └── .protokolo.toml
       └── .protokolo.toml

This represents the top section ``changelog.d`` containing two subsections
``added`` and ``fixed``. Each subsection has one fragment each. When compiled,
it might look a little like this:

.. code:: markdown

   ## 1.0.0 - 2023-11-08

   ### Added

   - Added feature `--foo`.

   ### Fixed

   - Fixed performance issues when handling big files.

.. _fragments:

Fragments
~~~~~~~~~

In fragment files, you can write any valid (or invalid) markup. If the fragment
does not end with a newline character, one is implicitly added during
compilation.

Fragments in the same section are sorted alphabetically by their file name stem
(i.e. the final file extension is removed). If you want to make sure that a
fragment appears first or last, you can prefix the file name with something like
``000_`` or ``zzz_`` respectively.

.. tip::

   Because of how the compilation works, you typically want to follow a few
   rules:

   - Do not start the fragment with a newline.
   - Do not include headings.
   - If the fragment represents a list item:

     - Start with a bullet, typically ``-`` or ``*``.
     - End the fragment with zero or one newline.

   - If the fragment represents a paragraph:

     - Adjust its file name to make it appear exactly where you want it to
       appear.
     - End the fragment with two newlines.

Global configuration
--------------------

You can configure various global options in a TOML file. Protokolo loads the
first match of the following files in your current working directory:

- ``.protokolo.toml``
- ``pyproject.toml``

The configuration values go in the ``[protokolo]`` table, or the
``[tool.protokolo]`` table for ``pyproject.toml``. An example configuration
looks like this:

.. code:: toml

   [protokolo]
   changelog = "CHANGELOG.md"
   directory = "changelog.d"
   markup = "markdown"

Various Protokolo subcommands will use the above values as default values,
saving you some time typing.

changelog
~~~~~~~~~

The path to your change log file. This is typically ``CHANGELOG``,
``CHANGELOG.md``, or ``CHANGELOG.rst``.

directory
~~~~~~~~~

The path to the directory that contains the change log fragments and
subsections. This is typically ``changelog.d``.

markup
~~~~~~

The markup language used by your change log file and change log fragments.
Available options are:

- ``markdown``
- ``restructuredtext``

.. _section-configuration:

Section configuration
---------------------

The ``.protokolo.toml`` file in each directory configures options of the
corresponding section. The file format is TOML. The configuration values go in
the ``[protokolo.section]`` table. An example configuration looks like this:

.. code:: toml

   [protokolo.section]
   title = "${version} - ${date}"
   level = 2
   order = 1
   miscellaneous = "your-value-here"

The options are used during compilation.

.. _title:

title
~~~~~

A string that contains the text of the section heading, for example "Added" or
"${version} - ${date}".

Words that are prefixed by ``$`` (e.g. ``$version``) or surrounded with ``${}``
(e.g. ``${version}``) can be replaced during compile time with ``--format key
value`` (e.g. ``--format version 1.0.0``). Alternatively, they can be replaced
by the values of other keys in the ``.protokolo.toml`` file. See the
:ref:`miscellaneous keys <miscellaneous-keys>` section.

``${date}`` is a special case. If its value is not defined anywhere, the value
of ``${date}`` is today’s date in the format ``YYYY-MM-DD``.

``${title}`` is not valid and will not be replaced by anything.

The formatting rules of the title are identical to the Python
:class:`string.Template` behaviour. Most pertinently, in order to write ``$`` to
the title, you have to type ``$$``.

If no title is defined, it is automatically replaced by the string "TODO: No
section title defined".

level
~~~~~

The level of the heading as an integer. This defaults to 1, or the value of the
parent level plus 1. This effectively means you really only need to define it
once in the top section; the levels of the subsections are increased as the
subdirectories are nested. You typically set this value to '2' in
``changelog.d/.protokolo.toml``.

.. note::

   There are no standard symbols assigned to levels in reStructuredText. They
   are supposed to be determined from the succession of headings. Because
   Protokolo is not an immensely smart tool, the levels are hardcoded to the
   levels used in Pandoc:

   - ``=`` for level 1.
   - ``-`` for level 2.
   - ``~`` for level 3.
   - ``^`` for level 4.
   - ``'`` for level 5.

order
~~~~~

An integer representing the priority in ordering for a section. This does
nothing for the top section.

(Sub)sections that share the same parent are normally sorted alphabetically by
their title. If subsections define this option, they are instead sorted by this
value, low-to-high. Sections that do not have this option defined are always
sorted after sections that do.

.. _miscellaneous-keys:

Miscellaneous keys
~~~~~~~~~~~~~~~~~~

You can define any key you want with any valid TOML value. Its value can be used
as part of the :ref:`formatting of the title <title>`, or for any other purpose.

Options
-------

.. option:: --help

    Display help and exit. If no command is provided, this option is implied.

.. option:: --version

    Display the version and exit.

Commands
--------

:manpage:`protokolo-compile(1)`
    Compile the contents of the change log directory into a change log file.

:manpage:`protokolo-init(1)`
    Set up your project for use with Protokolo with sane defaults.
