# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Main entry of program."""

from pathlib import Path

import click

from .compile import Section


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Protokolo is a change log generator."""
    ctx.ensure_object(dict)
    if ctx.default_map is None:
        ctx.default_map = {}

    if ctx.invoked_subcommand in ["compile"]:
        # TODO: Read default values from .protokolo.toml.
        ctx.default_map["compile"] = {
            # "changelog": "CHANGELOG",
            # "directory": Path("tmp"),
        }


@cli.command(name="compile")
@click.option(
    "--changelog",
    type=click.File("w", encoding="utf-8", lazy=True),
    required=True,
    show_default="determined by config",
    help="file into which to compile.",
)
@click.option(
    "--markup",
    default="markdown",
    type=click.Choice(["markdown", "restructuredtext"]),
    show_default="determined by config",
    help="markup language.",
)
@click.argument(
    "directory",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        path_type=Path,
    ),
    required=True,
)
@click.pass_context
def compile_(
    ctx: click.Context, changelog: click.File, markup: str, directory: Path
) -> None:
    """Compile a directory of change log entries into a CHANGELOG file.
    Directories and subdirectories are analogous to sections and subsections,
    and files are analogous to change log entries, typically paragraphs in a
    section.

    A change log directory should contain a '.protokolo.toml' file that defines
    some attributes of the section. This is an example file:

    \b
    [protokolo.section]
    title = "{version} - {date}"
    level = 2

    When the section is compiled, it looks a little like this:

    ## 1.0.0 - 2023-11-08

    The section header is followed by the contents of files in the section's
    directory. The file contents are pasted as-is into the section, separated as
    paragraphs. The entries are sorted alphabetically by file name. If you want
    a file to go first or last, prefix it with '000_' or 'zzz_'. Only files with
    your markup language's file extension (e.g. .md) are compiled as entries.

    If a section is empty (no change log entries), it is not compiled.

    The CHANGELOG file should contain the following comment, which is the
    location in the file where compiled sections will be pasted:

    <!-- protokolo-section-tag -->

    For more documentation and options, read the documentation at TODO.
    """
    section = Section.from_directory(directory)
    print(section.compile())
    print(ctx, changelog, markup)