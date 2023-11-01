# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Code to find-and-insert in CHANGELOG."""


def insert_into_str(text: str, target: str, lineno: int) -> str:
    """Insert *text* into *target* after *lineno*. *lineno* is 1-indexed.
    *lineno* 0 means inserting at the very start of *target*.
    """
    target_lines = target.splitlines()
    new_lines = (
        target_lines[:lineno] + [*text.splitlines()] + target_lines[lineno:]
    )
    return "\n".join(new_lines)


def find_first_occurrence(text: str, source: str) -> int | None:
    """Return the line number (1-indexed) of the first occurrence of *text* in
    *source*.

    Return None if no occurrence was found.
    """
    for lineno, line in enumerate(source.splitlines(), 1):
        if text in line:
            return lineno
    return None
