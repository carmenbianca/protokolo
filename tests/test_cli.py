# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the formatting code."""

from contextlib import contextmanager, suppress
from inspect import cleandoc
from pathlib import Path
from typing import Generator

from freezegun import freeze_time

import protokolo
from protokolo.cli import cli

# pylint: disable=unspecified-encoding


@contextmanager
def chmod(path: str | Path, mode: int) -> Generator[None, None, None]:
    """chmod as a context manager."""
    path = Path(path)
    try:
        old_mode = path.stat().st_mode
        path.chmod(mode)
        yield
    finally:
        with suppress(Exception):
            path.chmod(old_mode)  # pylint: disable=used-before-assignment


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


class TestInit:
    """Collect all tests for init."""

    def test_help_is_not_default(self, runner):
        """--help is not the default action."""
        without_help = runner.invoke(cli, ["init"])
        with_help = runner.invoke(cli, ["init", "--help"])
        assert without_help.output != with_help.output
        assert without_help.exit_code == 0
        assert with_help.exit_code == 0

    def test_simple(self, empty_runner):
        """Use without any parameters; correctly set up files."""
        result = empty_runner.invoke(cli, ["init"])
        assert result.exit_code == 0
        assert "# Change log" in Path("CHANGELOG.md").read_text()
        main_section_toml = Path("changelog.d/.protokolo.toml").read_text()
        assert "[protokolo.section]" in main_section_toml
        assert "title =" in main_section_toml
        assert "level = 2" in main_section_toml
        sections = [
            "added",
            "changed",
            "deprecated",
            "removed",
            "fixed",
            "security",
        ]
        for path in Path("changelog.d").iterdir():
            assert path.name in sections + [".protokolo.toml"]
        subsection_toml = Path("changelog.d/added/.protokolo.toml").read_text()
        assert "[protokolo.section]" in subsection_toml
        assert 'title = "Added"' in subsection_toml
        assert "order = 1" in subsection_toml
        for section in sections:
            assert Path(f"changelog.d/{section}/.protokolo.toml").is_file()

    def test_changelog_option(self, empty_runner):
        """Use with --changelog option."""
        result = empty_runner.invoke(cli, ["init", "--changelog", "CHANGELOG"])
        assert result.exit_code == 0
        assert "# Change log" in Path("CHANGELOG").read_text()
        assert not Path("CHANGELOG.md").exists()

    def test_markup_option(self, empty_runner):
        """Use with --markup option."""
        result = empty_runner.invoke(
            cli, ["init", "--markup", "restructuredtext"]
        )
        assert result.exit_code == 0
        assert (
            "==========\nChange log\n=========="
            in Path("CHANGELOG.md").read_text()
        )

    def test_directory_option(self, empty_runner):
        """Use with --directory option."""
        result = empty_runner.invoke(cli, ["init", "--directory", "foo"])
        assert result.exit_code == 0
        assert Path("foo").is_dir()
        assert Path("foo/.protokolo.toml").exists()
        assert not Path("changelog.d").exists()

    def test_run_twice(self, empty_runner):
        """Invoke twice without problems."""
        empty_runner.invoke(cli, ["init"])
        result = empty_runner.invoke(cli, ["init"])
        assert result.exit_code == 0

    def test_do_not_override(self, empty_runner):
        """Do not override contents of files."""
        empty_runner.invoke(cli, ["init"])
        Path("CHANGELOG.md").write_text("foo")
        Path("changelog.d/.protokolo.toml").write_text("foo")
        Path("changelog.d/added/.protokolo.toml").write_text("foo")
        result = empty_runner.invoke(cli, ["init"])
        assert result.exit_code == 0
        assert Path("CHANGELOG.md").read_text() == "foo"
        assert Path("changelog.d/.protokolo.toml").read_text() == "foo"
        assert Path("changelog.d/added/.protokolo.toml").read_text() == "foo"

    def test_oserror(self, empty_runner):
        """Handle OSErrors"""
        empty_runner.invoke(cli, ["init"])
        Path("changelog.d/added/.protokolo.toml").unlink()
        with chmod("changelog.d/added", 0o000):
            result = empty_runner.invoke(cli, ["init"])
        assert result.exit_code != 0
        assert "Permission denied" in result.output
