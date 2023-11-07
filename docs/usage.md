<!--
SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>

SPDX-License-Identifier: CC-BY-SA-4.0 OR GPL-3.0-or-later
-->

# Usage

For basic usage, please read the
[Usage section of the overview](project:./readme.md#usage).

## Global configuration

You can configure various global options in a TOML file. Protokolo loads the
first match of the following files in your current working directory:

- `.protokolo.toml`
- `pyproject.toml`

The configuration values go in the `[protokolo]` table, or the
`[tool.protokolo]` table for `pyproject.toml`. An example section looks like
this:

```toml
[protokolo]
changelog = "CHANGELOG.md"
directory = "changelog.d"
markup = "markdown"
```

Protokolo commands will use the values of the options as default values for
various subcommands, saving you some time typing.

### changelog

The path to your CHANGELOG file. This is typically CHANGELOG, CHANGELOG.md, or
CHANGELOG.rst.

### directory

The path to the directory that contains the change log entries and subsections.

### markup

The markup language used by your CHANGELOG file and change log entries.

## Section configuration

Each section (read: subdirectory) in your changelog.d directory has its own
`.protokolo.toml` configuration file. The top section (the changelog.d directory
itself) typically maps to the section of a version release in your CHANGELOG
file.

The configuration values go in the `[protokolo.section]` table. An example
section looks like this:

```toml
[protokolo.section]
title = "${version} - ${date}"
level = 2
# order = 1
```

The values of the options are used during compilation.

The inclusion of `.protokolo.toml` files is mandatory. If a directory does not
have such a file, it is not a section.

### title

A string that contains the text of the section heading, for example
"${title} -
${date}" or "Added".

Words that are prefixed by `$` (e.g. `$version`) or surrounded with `${}` (e.g.
`${version}`) can be replaced during compile time with `--format name=value`
(e.g. `--format version=1.0.0`).

`$date` is a special case. It is always replaced by today's date, but can be
overridden using the `--format` option. (TODO: not implemented yet)

If no title is defined, it is automatically replaced by the string "TODO: No
section title defined".

### level

The level of the heading as an integer. This defaults to 1, or the value of the
parent section plus 1. This effectively means you really only need to define it
once in the top section; the levels of the subsections are increased as the
subdirectories are nested.

TODO: reStructuredText heading symbols.

### order

An integer representing the priority in ordering for a section. This does
nothing for the top section.

(Sub)sections that share the same parent are normally sorted alphabetically by
their title. If subsections define this option, they are instead sorted by this
value, low-to-high. Sections that do not have this option defined are always
sorted after sections that do.

## Subcommands

### compile

This is the main subcommand of Protokolo. It gathers all your change log entry
files and aggregates them into a new section in CHANGELOG, after which the
change log entry files are deleted.

The file contents are pasted as-is into the section, separated as paragraphs.
The entries are sorted alphabetically by file name. If you want a file to go
first or last, prefix it with '000*' or 'zzz*'. Only files with your markup
language's file extension (e.g. `.md`) are compiled as entries.

The section is inserted two lines below the first instance of
`protokolo-section-tag` in the CHANGELOG file. The text should be in a comment
with space below available.

The [section configuration](#section-configuration) is used to define the
titles, levels, and ordering of sections and subsections.

### init

Quickly set up a project to be ready to use Protokolo. There is effectively no
configuration here, although the global configuration options are respected.
