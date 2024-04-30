..
  SPDX-FileCopyrightText: 2024 Carmen Bianca BAKKER <carmen@carmenbianca.eu>

  SPDX-License-Identifier: CC-BY-SA-4.0 OR GPL-3.0-or-later

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

For more information on how to use Protokolo beyond a reference of the
command-line options, see the accompanying documentation or read it at
`<https://protokolo.readthedocs.io>`_.

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
