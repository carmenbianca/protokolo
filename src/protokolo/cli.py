# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Main entry of program."""

import os
import tomllib
from io import TextIOWrapper
from pathlib import Path

import click

from ._formatter import MARKUP_EXTENSION_MAPPING as _MARKUP_EXTENSION_MAPPING
from .compile import Section
from .config import GlobalConfig
from .exceptions import (
    AttributeNotPositiveError,
    DictTypeError,
    HeaderFormatError,
)
from .replace import find_first_occurrence, insert_into_str
from .types import SupportedMarkup


@click.group(name="protokolo")
@click.version_option(package_name="protokolo")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Protokolo is a change log generator."""
    ctx.ensure_object(dict)
    if ctx.default_map is None:
        ctx.default_map = {}

    if ctx.invoked_subcommand in ["compile"]:
        # TODO: Make directory to search configurable.
        cwd = Path.cwd()
        config_path = GlobalConfig.find_config(Path.cwd())
        if config_path:
            config_path = config_path.relative_to(cwd)
            try:
                config = GlobalConfig.from_file(config_path)
            except (tomllib.TOMLDecodeError, DictTypeError, OSError) as error:
                raise click.UsageError(str(error)) from error
            ctx.default_map["compile"] = {
                "changelog": config.changelog,
                "markup": config.markup,
                "directory": config.directory,
            }


@cli.command(name="compile")
@click.option(
    "--changelog",
    type=click.File("r+", encoding="utf-8", lazy=True),
    required=True,
    show_default="determined by config",
    help="file into which to compile.",
)
@click.option(
    "--markup",
    default="markdown",
    type=click.Choice(SupportedMarkup.__args__),  # type: ignore
    show_default="determined by config, or markdown",
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
    ctx: click.Context,
    changelog: click.File,
    markup: SupportedMarkup,
    directory: Path,
) -> None:
    """Compile a directory of change log entries into a CHANGELOG file.
    Directories and subdirectories are analogous to sections and subsections,
    and files are analogous to change log entries, typically paragraphs in a
    section.

    A change log directory should contain a '.protokolo.toml' file that defines
    some attributes of the section. This is an example file:

    \b
    [protokolo.section]
    title = "${version} - ${date}"
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
    # TODO: use these args.
    for _ in (ctx,):
        pass

    # Create Section
    try:
        section = Section.from_directory(directory, markup=markup)
    except (
        tomllib.TOMLDecodeError,
        DictTypeError,
        AttributeNotPositiveError,
        OSError,
    ) as error:
        raise click.UsageError(str(error)) from error

    # Compile Section
    try:
        new_section = section.compile()
    except HeaderFormatError as error:
        raise click.UsageError(str(error)) from error

    if not new_section:
        click.echo("There are no change log entries to compile.")
        return

    # Write to CHANGELOG
    try:
        fp: TextIOWrapper
        with changelog.open() as fp:  # type: ignore
            # TODO: use buffer reading, probably
            contents = fp.read()
            # TODO: magic variable
            lineno = find_first_occurrence("protokolo-section-tag", contents)
            if lineno is None:
                raise click.UsageError(
                    f"There is no 'protokolo-section-tag' in"
                    f" {repr(changelog.name)}."
                )
            new_contents = insert_into_str(f"\n{new_section}", contents, lineno)
            fp.seek(0)
            fp.write(new_contents)
            fp.truncate()
    except OSError as error:
        # TODO: This is a little tricky to test. click already exits early if
        # changelog isn't readable/writable.
        raise click.UsageError(str(error))

    # Delete change log entries
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.suffix in _MARKUP_EXTENSION_MAPPING[markup]:
                path.unlink()
