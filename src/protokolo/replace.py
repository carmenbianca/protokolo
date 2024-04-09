# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Code to find-and-insert in CHANGELOG."""

# TODO: This code should probably be refactored to not rely on line count, but
# on character count.


def insert_into_str(text: str, target: str, lineno: int) -> str:
    """Insert *text* into *target* after *lineno*. *lineno* is 1-indexed.
    *lineno* 0 means inserting at the very start of *target*.

    A newline is automatically inserted after *text* if one is missing.
    """
    target_lines = target.splitlines(keepends=True)
    text_lines = [*text.splitlines(keepends=True)]
    # If the inserted text does not end with a newline, add one.
    if text_lines and not text_lines[-1].endswith("\n"):
        text_lines.append("\n")
    # Corner case for when inserting at the end, but the last character is not a
    # newline.
    if (
        lineno == len(target_lines)
        and target_lines
        and not target_lines[-1].endswith("\n")
    ):
        text_lines.insert(0, "\n")
    new_lines = target_lines[:lineno] + text_lines + target_lines[lineno:]
    return "".join(new_lines)


def find_first_occurrence(text: str, source: str) -> int | None:
    """Return the line number (1-indexed) of the first occurrence of *text* in
    *source*.

    Return :const:`None` if no occurrence was found.
    """
    for lineno, line in enumerate(source.splitlines(), 1):
        if text in line:
            return lineno
    return None
