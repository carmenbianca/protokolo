# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Code related to `protokolo init`."""

from pathlib import Path

from ._util import cleandoc
from .types import StrPath, SupportedMarkup

CHANGELOG_MD = """# Change log

This change log follows the [Keep a Changelog](http://keepachangelog.com/).
recommendations. Every release contains the following sections:

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for soon-to-be removed features.
- `Removed` for now removed features.
- `Fixed` for any bug fixes.
- `Security` in case of vulnerabilities.

<!-- protokolo-section-tag -->
"""
CHANGELOG_RST = """==========
Change log
==========

This change log follows the `Keep a Changelog <http://keepachangelog.com/>`_
recommendations. Every release contains the following sections:

- ``Added`` for new features.
- ``Changed`` for changes in existing functionality.
- ``Deprecated`` for soon-to-be removed features.
- ``Removed`` for now removed features.
- ``Fixed`` for any bug fixes.
- ``Security`` in case of vulnerabilities.

..
    protokolo-section-tag
"""


def create_changelog(
    changelog: StrPath, markup: SupportedMarkup | None
) -> None:
    """Create a changelog file"""
    changelog = Path(changelog).resolve()
    # Make certain the directory of CHANGELOG exists
    changelog.parent.mkdir(parents=True, exist_ok=True)
    # Make certain CHANGELOG exists, but do not overwrite it.
    if not changelog.exists():
        text = CHANGELOG_MD
        if markup == "restructuredtext":
            text = CHANGELOG_RST
        changelog.write_text(text, encoding="utf-8")


def create_keep_a_changelog(directory: StrPath) -> None:
    """Create a skeleton structure of changelog.d at *directory*."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    if not (directory / ".protokolo.toml").exists():
        (directory / ".protokolo.toml").write_text(
            cleandoc(
                """
                [protokolo.section]
                title = "${version} - ${date}"
                level = 2
                """
            ),
            encoding="utf-8",
        )
    subdirs = [
        {"dirname": "added", "title": "Added", "order": 1},
        {"dirname": "changed", "title": "Changed", "order": 2},
        {"dirname": "deprecated", "title": "Deprecated", "order": 3},
        {"dirname": "removed", "title": "Removed", "order": 4},
        {"dirname": "fixed", "title": "Fixed", "order": 5},
        {"dirname": "security", "title": "Security", "order": 6},
    ]
    for subdir in subdirs:
        (directory / str(subdir["dirname"])).mkdir(exist_ok=True)
        protokolo_toml = directory / str(subdir["dirname"]) / ".protokolo.toml"
        if not protokolo_toml.exists():
            protokolo_toml.write_text(
                cleandoc(
                    """
                    [protokolo.section]
                    title = "{title}"
                    order = {order}
                    """
                ).format(title=subdir["title"], order=subdir["order"]),
                encoding="utf-8",
            )


def create_root_toml(
    changelog: StrPath, markup: SupportedMarkup | None, directory: StrPath
) -> None:
    """Create a .protokolo.toml file in the current working directory."""
    if markup is None:
        markup = "markdown"

    Path(".protokolo.toml").write_text(
        cleandoc(
            """
            [protokolo]
            changelog = "{changelog}"
            markup = "{markup}"
            directory = "{directory}"
            """
        ).format(changelog=changelog, markup=markup, directory=directory),
        encoding="utf-8",
    )
