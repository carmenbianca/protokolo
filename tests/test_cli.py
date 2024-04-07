# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the formatting code."""

import errno
from inspect import cleandoc
from pathlib import Path

from freezegun import freeze_time

import protokolo
from protokolo import cli
from protokolo.cli import main
from protokolo.config import GlobalConfig, SectionAttributes

# pylint: disable=unspecified-encoding


def raise_permission(filename):
    """A context manager for a function that raises a permission error on
    *filename*.
    """

    def inner(*args, **kwargs):
        raise PermissionError(errno.EACCES, "Permission denied", filename)

    return inner


class TestMain:
    """Collect all tests for main."""

    def test_help_is_default(self, runner):
        """--help is optional."""
        without_help = runner.invoke(main, [])
        with_help = runner.invoke(main, ["--help"])
        assert without_help.output == with_help.output
        assert without_help.exit_code == with_help.exit_code == 0
        assert with_help.output.startswith("Usage: protokolo")

    def test_version(self, runner):
        """--version returns the correct version."""
        result = runner.invoke(main, ["--version"])
        assert result.output == f"protokolo, version {protokolo.__version__}\n"


class TestCompile:
    """Collect all tests for compile."""

    def test_help_is_not_default(self, runner):
        """--help is not the default action."""
        without_help = runner.invoke(main, ["compile"])
        with_help = runner.invoke(main, ["compile", "--help"])
        assert without_help.output != with_help.output
        assert without_help.exit_code != 0
        assert with_help.exit_code == 0

    @freeze_time("2023-11-08")
    def test_simple(self, runner):
        """The absolute simplest case without any configuration."""
        Path("changelog.d/foo.md").write_text("Foo")
        result = runner.invoke(
            main,
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

    @freeze_time("2023-11-08")
    def test_with_format(self, runner):
        """The simple case, but using --format."""
        Path("changelog.d/foo.md").write_text("Foo")
        result = runner.invoke(
            main,
            [
                "compile",
                "--changelog",
                "CHANGELOG.md",
                "--markup",
                "markdown",
                "--format",
                "version",
                "0.2.0",
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

                ## 0.2.0 - 2023-11-08

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
            main,
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
            main,
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

    def test_global_config_not_readable(self, runner, monkeypatch):
        """.protokolo.toml is not accessible (or any other OSError, really)."""
        Path(".protokolo.toml").touch()
        monkeypatch.setattr(
            GlobalConfig, "from_file", raise_permission(".protokolo.toml")
        )
        result = runner.invoke(
            main,
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
            main,
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
            main,
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
            main,
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

    def test_section_config_not_readable(self, runner, monkeypatch):
        """.protokolo.toml is not accessible (or any other OSError, really)."""
        Path("changelog.d/.protokolo.toml").touch()
        monkeypatch.setattr(
            SectionAttributes,
            "__init__",
            raise_permission("changelog.d/.protokolo.toml"),
        )
        result = runner.invoke(
            main,
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

    def test_heading_format_error(self, runner):
        """Could not format a heading."""
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
            main,
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
            "Error: Failed to format section heading of 'changelog.d': Heading"
            " level 10 is too deep." in result.output
        )

    def test_nothing_to_compile(self, runner):
        """There are no change log entries."""
        changelog = Path("CHANGELOG.md").read_text()
        result = runner.invoke(
            main,
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
            main,
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
            main,
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
            main,
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

    @freeze_time("2023-11-08")
    def test_dry_run(self, runner):
        """Test that no filesystem changes are made during dry run."""
        Path("changelog.d/foo.md").write_text("Foo")
        changelog_text = Path("CHANGELOG.md").read_text()

        result = runner.invoke(
            main,
            [
                "compile",
                "--changelog",
                "CHANGELOG.md",
                "--dry-run",
                "changelog.d",
            ],
        )
        assert result.exit_code == 0
        assert Path("CHANGELOG.md").read_text() == changelog_text
        assert Path("changelog.d/foo.md").exists()
        assert Path("changelog.d/foo.md").read_text() == "Foo"

        assert result.stdout.strip() == cleandoc(
            """
            # Change log

            Lorem ipsum.

            <!-- protokolo-section-tag -->

            ## ${version} - 2023-11-08

            Foo

            ## 0.1.0 - 2020-01-01

            First release.
            """
        )
        assert result.stdout.endswith("\n")


class TestInit:
    """Collect all tests for init."""

    def test_help_is_not_default(self, runner):
        """--help is not the default action."""
        without_help = runner.invoke(main, ["init"])
        with_help = runner.invoke(main, ["init", "--help"])
        assert without_help.output != with_help.output
        assert without_help.exit_code == 0
        assert with_help.exit_code == 0

    def test_simple(self, empty_runner):
        """Use without any parameters; correctly set up files."""
        result = empty_runner.invoke(main, ["init"])
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
        assert Path(".protokolo.toml").exists()
        root_toml = Path(".protokolo.toml").read_text()
        assert 'changelog = "CHANGELOG.md"' in root_toml
        assert 'markup = "markdown"' in root_toml
        assert 'directory = "changelog.d"' in root_toml

    def test_changelog_option(self, empty_runner):
        """Use with --changelog option."""
        result = empty_runner.invoke(main, ["init", "--changelog", "CHANGELOG"])
        assert result.exit_code == 0
        assert "# Change log" in Path("CHANGELOG").read_text()
        assert not Path("CHANGELOG.md").exists()
        assert (
            'changelog = "CHANGELOG"\n' in Path(".protokolo.toml").read_text()
        )

    def test_markup_option(self, empty_runner):
        """Use with --markup option."""
        result = empty_runner.invoke(
            main, ["init", "--markup", "restructuredtext"]
        )
        assert result.exit_code == 0
        assert (
            "==========\nChange log\n=========="
            in Path("CHANGELOG.md").read_text()
        )
        assert (
            'markup = "restructuredtext"' in Path(".protokolo.toml").read_text()
        )

    def test_directory_option(self, empty_runner):
        """Use with --directory option."""
        result = empty_runner.invoke(main, ["init", "--directory", "foo"])
        assert result.exit_code == 0
        assert Path("foo").is_dir()
        assert Path("foo/.protokolo.toml").exists()
        assert not Path("changelog.d").exists()
        assert 'directory = "foo"' in Path(".protokolo.toml").read_text()

    def test_run_twice(self, empty_runner):
        """Invoke twice without problems."""
        empty_runner.invoke(main, ["init"])
        result = empty_runner.invoke(main, ["init"])
        assert result.exit_code == 0

    def test_do_not_override(self, empty_runner):
        """Do not override contents of files."""
        empty_runner.invoke(main, ["init"])
        Path("CHANGELOG.md").write_text("foo")
        Path("changelog.d/.protokolo.toml").write_text("foo")
        Path("changelog.d/added/.protokolo.toml").write_text("foo")
        result = empty_runner.invoke(main, ["init"])
        assert result.exit_code == 0
        assert Path("CHANGELOG.md").read_text() == "foo"
        assert Path("changelog.d/.protokolo.toml").read_text() == "foo"
        assert Path("changelog.d/added/.protokolo.toml").read_text() == "foo"

    def test_oserror(self, empty_runner, monkeypatch):
        """Handle OSErrors"""
        empty_runner.invoke(main, ["init"])
        monkeypatch.setattr(
            cli,
            "create_keep_a_changelog",
            raise_permission("changelog.d"),
        )
        result = empty_runner.invoke(main, ["init"])
        assert result.exit_code != 0
        assert "Permission denied" in result.output
