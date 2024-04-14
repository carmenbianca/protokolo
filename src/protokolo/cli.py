# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Main entry of program."""

import gettext
import os
import tomllib
from inspect import cleandoc
from io import TextIOWrapper
from pathlib import Path

import click
from click.formatting import wrap_text

from ._formatter import MARKUP_EXTENSION_MAPPING as _MARKUP_EXTENSION_MAPPING
from .compile import Section
from .config import GlobalConfig
from .exceptions import (
    AttributeNotPositiveError,
    DictTypeError,
    HeadingFormatError,
    ProtokoloTOMLIsADirectoryError,
    ProtokoloTOMLNotFoundError,
)
from .i18n import _
from .initialise import (
    create_changelog,
    create_keep_a_changelog,
    create_root_toml,
)
from .replace import find_first_occurrence, insert_into_str
from .types import SupportedMarkup

# pylint: disable=missing-function-docstring

_PACKAGE_PATH = os.path.dirname(__file__)
_LOCALE_DIR = os.path.join(_PACKAGE_PATH, "locale")
if gettext.find("protokolo", localedir=_LOCALE_DIR):
    gettext.bindtextdomain("protokolo", _LOCALE_DIR)
    # This is needed to make Click recognise our translations. Our own
    # translations use the class-based API.
    gettext.textdomain("protokolo")


_VERSION_TEXT = (
    _("%(prog)s, version %(version)s")
    + "\n\n"
    + _(
        "This program is free software: you can redistribute it and/or modify"
        " it under the terms of the GNU General Public License as published by"
        " the Free Software Foundation, either version 3 of the License, or"
        " (at your option) any later version."
    )
    + _(
        "This program is distributed in the hope that it will be useful,"
        " but WITHOUT ANY WARRANTY; without even the implied warranty of"
        " MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the"
        " GNU General Public License for more details."
    )
    + "\n\n"
    + _(
        "You should have received a copy of the GNU General Public License"
        " along with this program. If not, see"
        " <https://www.gnu.org/licenses/>."
    )
    + "\n\n"
    + _("Written by Carmen Bianca BAKKER.")
)

_MAIN_HELP = _("Protokolo is a change log generator.")


@click.group(name="protokolo", help=_MAIN_HELP)
@click.version_option(
    package_name="protokolo",
    message=wrap_text(_VERSION_TEXT, preserve_paragraphs=True),
)
@click.pass_context
def main(ctx: click.Context) -> None:
    ctx.ensure_object(dict)
    if ctx.default_map is None:
        ctx.default_map = {}

    # Only load the global config if the subcommand needs it.
    if ctx.invoked_subcommand in ["compile", "init"]:
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


_COMPILE_HELP = (
    _(
        "Aggregate all change log fragments into a change log file. The"
        " fragments are gathered from a change log directory, and subsequently"
        " deleted."
    )
    + "\n\n"
    + _(
        "A change log directory should contain a '.protokolo.toml' file that"
        " defines some attributes of the section. This is an example file:"
    )
    + "\n\n"
    + cleandoc(
        """
        \b
        [protokolo.section]
        title = "${version} - ${date}"
        level = 2
        """
    )
    + "\n\n"
    + _("When the section is compiled, it looks a little like this:")
    + "\n\n"
    + "## 1.0.0 - 2023-11-08"
    + "\n\n"
    + _(
        "The heading is followed by the contents of files in the section's"
        " directory. If a section is empty (no change log fragments), it is not"
        " compiled."
    )
    + "\n\n"
    + cleandoc(
        """
        \b
        <!-- protokolo-section-tag -->
        """
    )
    + "\n\n"
    + _(
        "For more documentation and options, read the documentation at"
        " <https://protokolo.readthedocs.io>."
    )
)


@main.command(name="compile", help=_COMPILE_HELP)
@click.option(
    "--changelog",
    "-c",
    show_default=_("determined by config"),
    type=click.File("r+", encoding="utf-8", lazy=True),
    required=True,
    help=_("File into which to compile."),
)
@click.option(
    "--directory",
    "-d",
    show_default=_("determined by config"),
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        path_type=Path,
    ),
    required=True,
    help=_("Change log directory to compile."),
)
@click.option(
    "--markup",
    "-m",
    default="markdown",
    # TRANSLATORS: do not translate markdown.
    show_default=_("determined by config, or markdown"),
    type=click.Choice(SupportedMarkup.__args__),  # type: ignore
    help=_("Markup language."),
)
@click.option(
    "--format",
    "-f",
    "format_",
    type=(str, str),
    metavar="<KEY VALUE>...",
    multiple=True,
    # TRANSLATORS: string-format is a verb.
    help=_("Use key-value pairs to string-format section headings."),
)
@click.option(
    "--dry-run",
    "-n",
    is_flag=True,
    # TRANSLATORS: do not translate STDOUT.
    help=_("Do not write to file system; print result to STDOUT."),
)
def compile_(
    changelog: click.File,
    directory: Path,
    markup: SupportedMarkup,
    format_: tuple[tuple[str, str], ...],
    dry_run: bool,
) -> None:
    format_pairs: dict[str, str] = dict(format_)

    # Create Section
    try:
        section = Section.from_directory(
            directory, markup=markup, section_format_pairs=format_pairs
        )
    except (
        ProtokoloTOMLNotFoundError,
        ProtokoloTOMLIsADirectoryError,
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
        click.echo(_("There are no change log fragments to compile."))
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
                    # TRANSLATORS: do not translate protokolo-section-tag.
                    _("There is no 'protokolo-section-tag' in {path}.").format(
                        path=repr(changelog.name)
                    )
                )
            new_contents = insert_into_str(f"\n{new_section}", contents, lineno)
            if dry_run:
                click.echo(new_contents, nl=False)
            else:
                fp.seek(0)
                fp.write(new_contents)
                fp.truncate()
    except OSError as error:
        raise click.UsageError(str(error)) from error

    # Delete change log fragments
    if not dry_run:
        _delete_fragments(section)


_INIT_HELP = (
    _(
        "Set up your project to be ready to use Protokolo. It creates a change"
        " log file, a change log directory with subsections that match the Keep"
        " a Changelog recommendations, .protokolo.toml files with metadata for"
        " those (sub)sections, and a root .protokolo.toml file with defaults"
        " for subsequent Protokolo commands. Assuming defaults, the end result"
        " looks like this:"
    )
    + "\n\n"
    + cleandoc(
        """
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
        """
    )
    + "\n\n"
    + _(
        "Files that already exist are never overwritten, except the root"
        " .protokolo.toml file, which is always (re-)generated."
    )
)


@main.command(name="init", help=_INIT_HELP)
@click.option(
    "--changelog",
    "-c",
    default="CHANGELOG.md",
    # TRANSLATORS: do not translate CHANGELOG.md.
    show_default=_("determined by config, or CHANGELOG.md"),
    type=click.File("w", encoding="utf-8", lazy=True),
    help=_("Change log file to create."),
)
@click.option(
    "--directory",
    "-d",
    default="changelog.d",
    # TRANSLATORS: do not translate changelog.d.
    show_default=_("determined by config, or changelog.d"),
    type=click.Path(
        file_okay=False,
        dir_okay=True,
        readable=True,
        path_type=Path,
    ),
    help=_("Change log directory to create."),
)
@click.option(
    "--markup",
    "-m",
    default="markdown",
    # TRANSLATORS: do not translate markdown.
    show_default=_("determined by config, or markdown"),
    type=click.Choice(SupportedMarkup.__args__),  # type: ignore
    help=_("Markup language."),
)
def init(
    changelog: click.File,
    directory: Path,
    markup: SupportedMarkup,
) -> None:
    try:
        create_changelog(changelog.name, markup)
        create_keep_a_changelog(directory)
        create_root_toml(changelog.name, markup, directory)
    except OSError as error:
        raise click.UsageError(str(error)) from error


def _delete_fragments(section: Section) -> None:
    """Delete :class:`.compile.Fragment`s' source files recursively."""
    for fragment in section.fragments:
        if fragment.source:
            fragment.source.unlink(missing_ok=True)
    for subsection in section.subsections:
        _delete_fragments(subsection)
