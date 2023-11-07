# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Some miscellaneous utilities."""

from collections.abc import Callable, Mapping
from inspect import cleandoc
from pathlib import Path
from types import UnionType
from typing import Any

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


def type_in_expected_type(value: type, expected_type: type | UnionType) -> bool:
    """Check whether the type *value* matches any of *expected_type*.

    >>> type_in_expected_type(int, int)
    True
    >>> type_in_expected_type(str, str | bytes)
    True
    >>> type_in_expected_type(str, float | int)
    False
    """
    return (isinstance(expected_type, type) and value is expected_type) or (
        isinstance(expected_type, UnionType) and value in expected_type.__args__
    )


def nested_itemgetter(*path: Any) -> Callable[[Mapping[Any, Any]], Any]:
    """A nested implementation of operator.itemgetter.

    >>> config = {"hello": {"world": "foo"}}
    >>> nested_itemgetter("hello", "world")(config)
    'foo'

    Raises:
        KeyError: if any of the path items doesn't exist in the nested
            structure.
    """

    def browse(values: Mapping[Any, Any]) -> Any:
        for item in path:
            values = values[item]
        return values

    return browse


def create_changelog(
    changelog: StrPath, markup: SupportedMarkup | None
) -> None:
    """Create a changelog file"""
    changelog = Path(changelog).resolve()
    # Make certain the directory of CHANGELOG exists
    changelog.parent.mkdir(parents=True, exist_ok=True)
    # Make certain CHANGELOG exists.
    if not changelog.exists():
        if markup == "restructuredtext":
            changelog.write_text(CHANGELOG_RST)
        else:
            changelog.write_text(CHANGELOG_MD)


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
            )
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
                ).format(title=subdir["title"], order=subdir["order"])
            )
