# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Some typing definitions."""

from datetime import date, datetime
from os import PathLike
from types import UnionType
from typing import Literal, Mapping

StrPath = str | PathLike

SupportedMarkup = Literal["markdown", "restructuredtext"]

TOMLType = Mapping[str, "TOMLValue"]
TOMLValue = (
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
TOMLValueType: UnionType = (
    str | int | float | bool | datetime | date | None | list | dict
)

NestedTypeDict = Mapping[str, "NestedTypeValue"]
NestedTypeValue = type | UnionType | NestedTypeDict
