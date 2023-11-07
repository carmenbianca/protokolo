# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Fixtures and stuff."""

from inspect import cleandoc
from pathlib import Path

import pytest
from click.testing import CliRunner

# pylint: disable=unused-argument


@pytest.fixture()
def project_dir(tmpdir_factory, monkeypatch) -> Path:
    """Create a temporary project directory."""
    directory = Path(str(tmpdir_factory.mktemp("project_dir")))

    (directory / "CHANGELOG.md").write_text(
        cleandoc(
            """
            # Change log

            Lorem ipsum.

            <!-- protokolo-section-tag -->

            ## 0.1.0 - 2020-01-01

            First release.
            """
        )
    )
    (directory / "CHANGELOG.rst").write_text(
        cleandoc(
            """
            ==========
            Change log
            ==========

            Lorem ipsum.

            ..
                protokolo-section-tag

            0.1.0 - 2020-01-01
            ==================

            First release.
            """
        )
    )

    changelog_d = directory / "changelog.d"
    changelog_d.mkdir()
    (changelog_d / ".protokolo.toml").write_text(
        cleandoc(
            """
            [protokolo.section]
            title = "${version} - ${date}"
            level = 2
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

    monkeypatch.chdir(directory)
    return directory


@pytest.fixture()
def empty_dir(tmpdir_factory, monkeypatch) -> Path:
    """Create a temporary empty directory."""
    directory = Path(str(tmpdir_factory.mktemp("project_dir")))
    monkeypatch.chdir(directory)
    return directory


@pytest.fixture()
def runner(project_dir) -> CliRunner:
    """Return a :class:`CliRunner` for a :func:`project_dir`."""
    return CliRunner()


@pytest.fixture()
def empty_runner(empty_dir) -> CliRunner:
    """Return a :class:`CliRunner` for an :func:`empty_dir`."""
    return CliRunner()
