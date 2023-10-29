# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Fixtures and stuff."""

from collections.abc import Generator
from inspect import cleandoc, isclass
from pathlib import Path

import pytest

from protokolo import _formatter
from protokolo._formatter import MarkupFormatter

formatter_classes = [
    cls
    for cls in _formatter.__dict__.values()
    if isclass(cls)
    and issubclass(cls, MarkupFormatter)
    and cls is not MarkupFormatter
]


@pytest.fixture(scope="session", params=formatter_classes)
def formatter(request) -> Generator[MarkupFormatter, None, None]:
    """Return a formatter class."""
    yield request.param


@pytest.fixture()
def project_dir(tmpdir_factory) -> Path:
    """Create a temporary project directory."""
    directory = Path(str(tmpdir_factory.mktemp("project_dir")))
    changelog_d = directory / "changelog.d"
    changelog_d.mkdir()
    (changelog_d / ".protokolo.toml").write_text(
        cleandoc(
            """
            [protokolo.section]
            title = "${version} - ${date}"
            """
        )
    )
    feature_section = changelog_d / "feature"
    feature_section.mkdir()
    (feature_section / ".protokolo.toml").write_text(
        cleandoc(
            """
            [protokolo.section]
            title = "Features"
            """
        )
    )

    return directory
