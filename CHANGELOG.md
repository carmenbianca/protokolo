<!--
SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>

SPDX-License-Identifier: CC-BY-SA-4.0 OR GPL-3.0-or-later
-->

# Change log

This change log follows the [Keep a Changelog](http://keepachangelog.com/)
recommendations. Every release contains the following sections:

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for soon-to-be removed features.
- `Removed` for now removed features.
- `Fixed` for any bug fixes.
- `Security` in case of vulnerabilities.

The versions follow [semantic versioning](https://semver.org) for the
`protokolo` CLI command and its behaviour. There are no guarantees of stability
for the `protokolo` Python library.

<!-- protokolo-section-tag -->

## 1.0.1 - 2024-04-09

### Fixed

- Include `docs/` in the sdist.

## 1.0.0 - 2024-04-09

### Changed

- Renamed the concept of 'entry' to 'fragment'.
- Changed the way newlines are handled for fragments. Newlines surrounding
  fragments are now significant when concatenation of fragments happens.
  However, a _lack_ of final is considered an error, and one is always added.
  The foremost consequence of this change is that list items now concatenate
  without a blank line between them.

### Fixed

- Newline at the end of CHANGELOG is retained after `protokolo compile`.

## 0.3.0 - 2024-04-07

### Added

- Added `--dry-run` to `compile`.
- Added `--format` to `compile`. This is primarily useful for doing something
  like `protokolo compile --format version 1.0.0` to format the correct version
  into the section heading.

### Changed

- Re-wrote the internals to use the `attrs` library for easier validation.

## 0.2.0 - 2023-11-07

This is the prototype release of Protokolo. It contains the most basic
functionality and limited documentation, but is a minimum viable product. You
can:

- Compile the `changelog.d` directory into a CHANGELOG file with
  `protokolo compile`.
- Create the `changelog.d` directory with `protokolo init`.
- Configure some bits and bobs in `.protokolo.toml` files.
- Use both Markdown and reStructuredText.

## 0.1.0 - 2023-10-20

This release doesn't contain much of anything. I made it to claim the namespace
on PyPI.
