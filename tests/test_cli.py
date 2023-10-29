# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the formatting code."""

import protokolo
from protokolo.cli import cli, compile_

# pylint: disable=too-few-public-methods


class TestCli:
    """Collect all tests for cli."""

    def test_help_is_default(self, runner):
        """--help is optional."""
        without_help = runner.invoke(cli, [])
        with_help = runner.invoke(cli, ["--help"])
        assert without_help.output == with_help.output
        assert without_help.exit_code == with_help.exit_code == 0

    def test_version(self, runner):
        """--version returns the correct version."""
        result = runner.invoke(cli, ["--version"])
        assert result.output == f"protokolo, version {protokolo.__version__}\n"


class TestCompile:
    """Collect all tests for compile."""

    def test_help_is_not_default(self, runner):
        """--help is not the default action."""
        without_help = runner.invoke(compile_, [])
        with_help = runner.invoke(compile_, ["--help"])
        assert without_help.output != with_help.output
        assert without_help.exit_code != 0
        assert with_help.exit_code == 0
