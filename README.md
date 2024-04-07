<!--
SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>

SPDX-License-Identifier: CC-BY-SA-4.0 OR GPL-3.0-or-later
-->

# Protokolo

[![Latest Protokolo version](https://img.shields.io/pypi/v/protokolo.svg)](https://pypi.python.org/pypi/protokolo)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/protokolo.svg)](https://pypi.python.org/pypi/protokolo)
[![REUSE status](https://api.reuse.software/badge/codeberg.org/carmenbianca/protokolo)](https://api.reuse.software/info/codeberg.org/carmenbianca/protokolo)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg)](https://github.com/RichardLitt/standard-readme)

Protokolo is a change log generator.

Protokolo allows you to maintain your change log entries in separate files, and
then finally aggregate them into a new section in CHANGELOG just before release.

## Table of Contents

- [Background](#background)
- [Install](#install)
- [Usage](#usage)
- [Maintainers](#maintainers)
- [Contributing](#contributing)
- [License](#license)

## Background

Change logs are [a really good idea](https://keepachangelog.com/).
Unfortunately, they are also a bit of a pain when combined with version control:

- If two pull requests edit CHANGELOG, there is a non-zero chance that you'll
  need to resolve a conflict when trying to merge them both.
- Just after you make a release, you need to create a new section in CHANGELOG
  for your next release. If you forget this busywork, new feature branches will
  need to create this section, which increases the chance of merge conflicts.
- If a feature branch adds a change log entry to the section for the next v1.2.3
  release, and v1.2.3 subsequently releases without merging that feature branch,
  then merging that feature branch afterwards would still add the change log
  entry to the v1.2.3 section, even though it should now go to the v1.3.0
  section.

Life would be a lot easier if you didn't have to deal with these problems.

Enter Protokolo. The idea is very simple: For every change log entry, create a
new file. Finally, just before release, compile the contents of those files into
a new section in CHANGELOG, and delete the files.

## Install

Protokolo is a regular Python package. You can install it using
`pipx install protokolo`. Make sure that `~/.local/share/bin` is in your `$PATH`
with `pipx ensurepath`.

## Usage

For full documentation and options, read the documentation at TODO.

### Initial set-up

To set up your project for use with Protokolo, run `protokolo init`. This will
create a `CHANGELOG.md` file (if one did not already exist) and a directory
structure under `changelog.d`. The directory structure uses the
[Keep a Changelog](https://keepachangelog.com/) sections, and ends up looking
like this:

```
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
```

The `.protokolo.toml` files in `changelog.d` contain metadata for their
respective sections; the section title, heading level, and order. Their
inclusion is mandatory.

The `.protokolo.toml` file in the root of the project contains configurations
for Protokolo that reduce the amount of typing you need to do when running
commands.

If a `CHANGELOG.md` file already existed, make sure to add a line containing
`<!-- protokolo-section-tag -->` just before the heading of the latest release.

### Adding entries

To add a change log entry, create the file `changelog.d/added/my_feature.md`,
and write something like:

```markdown
- Added `--my-new-feature` option.
```

Note the item dash at the start; Protokolo does not add them for you. What you
write is exactly what you get.

You can add more files. Change log entries in the same section (read: directory)
are sorted alphabetically by their file name. If you want to make certain that
some change log entries go first or last, prefix the file with `000_` or `zzz_`.
For example, you can create `changelog.d/added/000_important_feature.md` to make
it appear first.

### Compiling your change log

You compile your change log with `protokolo compile`. This will take all change
log entries from `changelog.d` and put them in your `CHANGELOG.md`. If we run it
now, the following section is added after the `<!-- protokolo-section-tag -->`
comment:

```markdown
## ${version} - 2023-11-08

### Added

- Added important feature.

- Added `--my-new-feature` option.
```

The Markdown files in `changelog.d/added/` are deleted. You can manually replace
`${version}` with a release version, or you can pass the option
`--format version 1.0.0` to `protokolo compile` to format the heading at compile
time.

## Maintainers

- Carmen Bianca BAKKER <carmen@carmenbianca.eu>

## Contributing

The code and issue tracker is hosted at
<https://codeberg.org/carmenbianca/protokolo>. You are welcome to open any
issues. For pull requests, bug fixes are always welcome, but new features should
probably be discussed in any issue first.

## License

All code is licensed under GPL-3.0-or-later.

All documentation is licensed under CC-BY-SA-4.0 OR GPL-3.0-or-later.

Some configuration files are licensed under CC0-1.0 OR GPL-3.0-or-later.

The repository is [REUSE](https://reuse.software)-compliant. Check the
individual files for their exact licensing.
