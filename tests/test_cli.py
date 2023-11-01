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
        assert not Path("changelog.d/foo.md").exists()

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
        assert "Error: Invalid TOML in '.protokolo.toml'" in result.output

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
        assert (
            "Error: .protokolo.toml: 'changelog' does not have the correct"
            " type. Expected str | None. Got 1."
        ) in result.output

    def test_global_config_not_readable(self, runner):
        """.protokolo.toml is not readable (or any other OSError, really)."""
        Path(".protokolo.toml").touch()
        Path(".protokolo.toml").chmod(0o100)  # write-only
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
        assert "Permission denied" in result.output

    def test_section_config_parse_error(self, runner):
        """.protokolo.toml cannot be parsed."""
        Path("changelog.d/.protokolo.toml").write_text("{'Foo")
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
            "Error: Invalid TOML in 'changelog.d/.protokolo.toml'"
            in result.output
        )

    def test_section_config_wrong_type(self, runner):
        """An element has the wrong type."""
        Path("changelog.d/.protokolo.toml").write_text(
            cleandoc(
                """
                [protokolo.section]
                title = 1
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
        assert (
            "Error: changelog.d/.protokolo.toml:"
            " 'title' does not have the correct type. Expected str. Got 1."
        ) in result.output

    def test_section_config_not_positive(self, runner):
        """An element has should be positive."""
        Path("changelog.d/.protokolo.toml").write_text(
            cleandoc(
                """
                [protokolo.section]
                level = -1
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
        assert (
            "Error: Wrong value in 'changelog.d/.protokolo.toml': level must be"
            " a positive integer, got -1" in result.output
        )

    def test_section_config_not_readable(self, runner):
        """.protokolo.toml is not readable (or any other OSError, really)."""
        Path("changelog.d/.protokolo.toml").touch()
        Path("changelog.d/.protokolo.toml").chmod(0o100)  # write-only
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
        assert "Permission denied" in result.output

    def test_header_format_error(self, runner):
        """Could not format a header."""
        Path("changelog.d/.protokolo.toml").write_text(
            cleandoc(
                """
                [protokolo.section]
                level = 10
                """
            )
        )
        Path("changelog.d/foo.rst").write_text("Foo")
        result = runner.invoke(
            cli,
            [
                "compile",
                "--changelog",
                "CHANGELOG.rst",
                "--markup",
                "restructuredtext",
                "changelog.d",
            ],
        )
        assert result.exit_code != 0
        assert (
            "Error: Failed to format section header of 'changelog.d': Header"
            " level 10 is too deep." in result.output
        )

    def test_nothing_to_compile(self, runner):
        """There are no change log entries."""
        changelog = Path("CHANGELOG.md").read_text()
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
        assert result.output == "There are no change log entries to compile.\n"
        assert Path("CHANGELOG.md").read_text() == changelog

    def test_no_replacement_tag(self, runner):
        """There is no protokolo-section-tag in CHANGELOG."""
        Path("CHANGELOG.md").write_text("Hello, world!")
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
        assert result.exit_code != 0
        assert (
            "Error: There is no 'protokolo-section-tag' in 'CHANGELOG.md'"
            in result.output
        )

    @freeze_time("2023-11-08")
    def test_nested_entries_deleted(self, runner):
        """Entries in nested sections are also deleted, but other files are
        not.
        """
        Path("changelog.d/feature/foo.md").write_text("Foo")
        Path("changelog.d/feature/bar.txt").write_text("Bar")
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

                ### Features

                Foo

                ## 0.1.0 - 2020-01-01
                """
            )
            in changelog
        )
        assert not Path("changelog.d/feature/foo.md").exists()
        assert Path("changelog.d/feature/bar.txt").exists()

    @freeze_time("2023-11-08")
    def test_restructuredtext(self, runner):
        """A simple test, but for restructuredtext."""
        Path("changelog.d/foo.rst").write_text("Foo")
        Path("changelog.d/feature/bar.rst").write_text("Bar")
        result = runner.invoke(
            cli,
            [
                "compile",
                "--changelog",
                "CHANGELOG.rst",
                "--markup",
                "restructuredtext",
                "changelog.d",
            ],
        )
        assert result.exit_code == 0
        changelog = Path("CHANGELOG.rst").read_text()

        assert (
            cleandoc(
                """
                Lorem ipsum.

                ..
                    protokolo-section-tag

                ${version} - 2023-11-08
                =======================

                Foo

                Features
                --------

                Bar

                0.1.0 - 2020-01-01
                ==================
                """
            )
            in changelog
        )
        assert not Path("changelog.d/feature/bar.rst").exists()
        assert not Path("changelog.d/foo.rst").exists()
