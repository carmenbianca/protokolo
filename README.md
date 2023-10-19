<!--
SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>

SPDX-License-Identifier: CC-BY-SA-4.0 OR GPL-3.0-or-later
-->

# Protokolo

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

TODO

## Usage

TODO

## Maintainers

- Carmen Bianca BAKKER <carmen@carmenbianca.eu>

## Contributing

TODO

## License

All code is licensed under GPL-3.0-or-later.

All documentation is licensed under CC-BY-SA-4.0 OR GPL-3.0-or-later.

Some configuration files are licensed under CC0-1.0 OR GPL-3.0-or-later.

The repository is [REUSE](https://reuse.software)-compliant. Check the
individual files for their exact licensing.
