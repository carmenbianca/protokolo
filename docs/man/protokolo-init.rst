..
  SPDX-FileCopyrightText: 2024 Carmen Bianca BAKKER <carmen@carmenbianca.eu>

  SPDX-License-Identifier: CC-BY-SA-4.0 OR GPL-3.0-or-later

protokolo-init
==============

Synopsis
--------

**protokolo init** [*options*]

Description
-----------

:program:`protokolo init` sets up your project to be ready to use Protokolo
using defaults recommended by `Keep a Changelog <https://keepachangelog.com>`_.
It sets up three things:

- A change log file.
- A change log directory.
- A ``.protokolo.toml`` global configuration file in your current working
  directory.

Assuming the defaults are not changed, the result looks like this::

    .
    ├── changelog.d
    │   ├── added
    │   │   └── .protokolo.toml
    │   ├── changed
    │   │   └── .protokolo.toml
    │   ├── deprecated
    │   │   └── .protokolo.toml
    │   ├── fixed
    │   │   └── .protokolo.toml
    │   ├── removed
    │   │   └── .protokolo.toml
    │   ├── security
    │   │   └── .protokolo.toml
    │   └── .protokolo.toml
    ├── CHANGELOG.md
    └── .protokolo.toml

Files that already exist are never overwritten, except the root
``.protokolo.toml`` file, which is always (re-)generated.

Options with defaults
---------------------

If the below options are not defined, they default to the corresponding options
in the ``.protokolo.toml`` global configuration file if one exists, or otherwise
their base defaults. Both the defaults and the specified options are written
back to ``.protokolo.toml``.

.. option:: -c, --changelog

    Path to the change log file to be generated. Defaults to ``CHANGELOG.md``.

.. option:: -d, --directory

    Path to the change log directory to be generated. Defaults to
    ``changelog.d``.

.. option:: -m, --markup

    Markup language to use. This determines the contents of the generated change
    log file. Defaults to ``markdown``.

Other options
-------------

.. option:: --help

    Display help and exit.
