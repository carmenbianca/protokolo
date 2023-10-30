# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the formatting code."""

from inspect import cleandoc
from pathlib import Path

from freezegun import freeze_time

import protokolo
from protokolo.cli import cli

# pylint: disable=unspecified-encoding


class TestCli:
    """Collect all tests for cli."""

    def test_help_is_default(self, runner):
        """--help is optional."""
        without_help = runner.invoke(cli, [])
        with_help = runner.invoke(cli, ["--help"])
        assert without_help.output == with_help.output
        assert without_help.exit_code == with_help.exit_code == 0
        assert with_help.output.startswith("Usage: protokolo")

    def test_version(self, runner):
        """--version returns the correct version."""
        result = runner.invoke(cli, ["--version"])
        assert result.output == f"protokolo, version {protokolo.__version__}\n"


class TestCompile:
    """Collect all tests for compile."""

    def test_help_is_not_default(self, runner):
        """--help is not the default action."""
        without_help = runner.invoke(cli, ["compile"])
        with_help = runner.invoke(cli, ["compile", "--help"])
        assert without_help.output != with_help.output
        assert without_help.exit_code != 0
        assert with_help.exit_code == 0

    @freeze_time("2023-11-08")
    def test_simple(self, runner):
        """The absolute simplest case without any configuration."""
        Path("changelog.d/foo.md").write_text("Foo")
        result = runner.invoke(
            cli,
            [
                "compile",
                "--changelog",
                "CHANGELOG.md",
                "--markup",
                "markdown",
                "changelog.d",
            ],
        )
        assert result.exit_code == 0
        changelog = Path("CHANGELOG.md").read_text()
        assert (
            cleandoc(
                """
            Lorem ipsum.

            <!-- protokolo-section-tag -->

            ## ${version} - 2023-11-08

            Foo

            ## 0.1.0 - 2020-01-01
            """
            )
            in changelog
        )

    def test_global_config_parse_error(self, runner):
        """.protokolo.toml cannot be parsed."""
        Path(".protokolo.toml").write_text("{'Foo")
        result = runner.invoke(
            cli,
            [
                "compile",
                "--changelog",
                "CHANGELOG.md",
                "--markup",
                "markdown",
                "changelog.d",
            ],
        )
        assert result.exit_code != 0
        assert (
            f"Error: Invalid TOML in"
            f" {repr(str(Path('.protokolo.toml').absolute()))}" in result.output
        )

    def test_global_config_wrong_type(self, runner):
        """An element has the wrong type."""
        Path(".protokolo.toml").write_text(
            cleandoc(
                """
                [protokolo]
                changelog = 1
                """
            )
        )
        result = runner.invoke(
            cli,
            [
                "compile",
                "--changelog",
                "CHANGELOG.md",
                "--markup",
                "markdown",
                "changelog.d",
            ],
        )
        assert result.exit_code != 0
        # TODO: finish writing this test. the source of the file needs to be
        # shown in the error.