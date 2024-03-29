# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Some typing definitions."""

from datetime import date, datetime
from os import PathLike
from types import UnionType
from typing import Literal, Mapping, TypeAlias

# pylint: disable=invalid-name

#: Anything that looks like a path.
StrPath: TypeAlias = str | PathLike

#: The supported markup languages.
SupportedMarkup: TypeAlias = Literal["markdown", "restructuredtext"]

#: A TOML dictionary.
TOMLType: TypeAlias = Mapping[str, "TOMLValue"]
#: All possible types for a value in a TOML dictionary.
TOMLValue: TypeAlias = (
    str
    | int
    | float
    | bool
    | datetime
    | date
    | None
    | TOMLType
    | list["TOMLType"]
)
#: Like :ref:`TOMLValue`, but using only Python primitives.
TOMLValueType: UnionType = (
    str | int | float | bool | datetime | date | None | dict | list
)
