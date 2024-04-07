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
    HeadingFormatError,
)
from .initialise import (
    create_changelog,
    create_keep_a_changelog,
    create_root_toml,
)
from .replace import find_first_occurrence, insert_into_str
from .types import SupportedMarkup


@click.group(name="protokolo")
@click.version_option(package_name="protokolo")
@click.pass_context
def main(ctx: click.Context) -> None:
    """Protokolo is a change log generator."""
    ctx.ensure_object(dict)
    if ctx.default_map is None:
        ctx.default_map = {}

    # Only load the global config if the subcommand needs it.
    if ctx.invoked_subcommand in ["compile", "init"]:
        # TODO: Make directory to search configurable.
        cwd = Path.cwd()
        config_path = GlobalConfig.find_config(Path.cwd())
        if config_path:
            config_path = config_path.relative_to(cwd)
            try:
                config = GlobalConfig.from_file(config_path)
            except (tomllib.TOMLDecodeError, DictTypeError, OSError) as error:
                raise click.UsageError(str(error)) from error
            # TODO: reuse this repetition maybe?
            ctx.default_map["compile"] = {
                "changelog": config.changelog,
                "markup": config.markup,
                "directory": config.directory,
            }
            ctx.default_map["init"] = {
                "changelog": config.changelog,
                "markup": config.markup,
                "directory": config.directory,
            }


@main.command(name="compile")
@click.option(
    "--changelog",
    show_default="determined by config",
    type=click.File("r+", encoding="utf-8", lazy=True),
    required=True,
    help="File into which to compile.",
)
@click.option(
    "--markup",
    default="markdown",
    show_default="determined by config, or markdown",
    type=click.Choice(SupportedMarkup.__args__),  # type: ignore
    help="Markup language.",
)
@click.option(
    "--format",
    "-f",
    "format_",
    type=(str, str),
    metavar="<KEY VALUE>...",
    multiple=True,
    help="Use key-value pairs to string-format section headers.",
)
@click.option(
    "--dry-run",
    "-n",
    is_flag=True,
    help="Do not write to file system; print to STDOUT.",
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
def compile_(
    changelog: click.File,
    markup: SupportedMarkup,
    format_: tuple[tuple[str, str], ...],
    dry_run: bool,
    directory: Path,
) -> None:
    """Aggregate all change log entries from files in a directory into a
    CHANGELOG file.

    A change log directory should contain a '.protokolo.toml' file that defines
    some attributes of the section. This is an example file:

    \b
    [protokolo.section]
    title = "${version} - ${date}"
    level = 2

    When the section is compiled, it looks a little like this:

    ## 1.0.0 - 2023-11-08

    The heading is followed by the contents of files in the section's directory.
    If a section is empty (no change log entries), it is not compiled.

    The CHANGELOG file should contain the following comment, which is the
    location in the file after which the compiled section will be pasted:

    \b
    <!-- protokolo-section-tag -->

    For more documentation and options, read the documentation at TODO.
    """
    # TODO: Maybe split this up.
    # pylint: disable=too-many-locals
    format_pairs: dict[str, str] = dict(format_)

    # Create Section
    try:
        section = Section.from_directory(
            directory, markup=markup, section_format_pairs=format_pairs
        )
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
    except HeadingFormatError as error:
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
            if dry_run:
                click.echo(new_contents)
            else:
                fp.seek(0)
                fp.write(new_contents)
                fp.truncate()
    except OSError as error:
        # TODO: This is a little tricky to test. click already exits early if
        # changelog isn't readable/writable.
        raise click.UsageError(str(error))

    # Delete change log entries
    if not dry_run:
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                path = Path(dirpath) / filename
                if path.suffix in _MARKUP_EXTENSION_MAPPING[markup]:
                    path.unlink()


@main.command(name="init")
@click.option(
    "--changelog",
    default="CHANGELOG.md",
    show_default="determined by config, or CHANGELOG.md",
    type=click.File("w", encoding="utf-8", lazy=True),
    help="CHANGELOG file to create.",
)
@click.option(
    "--directory",
    default="changelog.d",
    show_default="determined by config, or changelog.d",
    type=click.Path(
        file_okay=False,
        dir_okay=True,
        readable=True,
        path_type=Path,
    ),
    help="Directory of change log sections and entries.",
)
@click.option(
    "--markup",
    default="markdown",
    show_default="determined by config, or markdown",
    type=click.Choice(SupportedMarkup.__args__),  # type: ignore
    help="Markup language.",
)
def init(
    changelog: click.File,
    directory: Path,
    markup: SupportedMarkup,
) -> None:
    """Set up your project to be ready to use Protokolo. It creates a
    CHANGELOG.md file, a changelog.d directory with subsections that match the
    Keep a Changelog recommendations, and .protokolo.toml files with metadata
    for those (sub)sections. The end result looks a little like this:

    \b
    .
    ├── changelog.d
    │   ├── added
    │   │   └── .protokolo.toml
    │   ├── changed
    │   │   └── .protokolo.toml
    │   ├── deprecated
    │   │   └── .protokolo.toml
    │   ├── fixed
    │   │   └── .protokolo.toml
    │   ├── removed
    │   │   └── .protokolo.toml
    │   ├── security
    │   │   └── .protokolo.toml
    │   └── .protokolo.toml
    ├── CHANGELOG.md
    └── .protokolo.toml

    Files that already exist are never overwritten, except the root
    .protokolo.toml file, which is always (re-)generated.
    """
    try:
        create_changelog(changelog.name, markup)
        create_keep_a_changelog(directory)
        create_root_toml(changelog.name, markup, directory)
    except OSError as error:
        raise click.UsageError(str(error))
