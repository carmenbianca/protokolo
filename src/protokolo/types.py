# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Some typing definitions."""

from os import PathLike
from typing import Literal

StrPath = str | PathLike
SupportedMarkup = Literal["markdown", "restructuredtext"]
