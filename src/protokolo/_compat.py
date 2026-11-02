# SPDX-FileCopyrightText: 2026 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: EUPL-1.2+

"""Helper functions for supporting multiple versions of Python
simultaneously.
"""

import sys
from typing import Any

PY_3_14_PLUS = sys.version_info[:2] >= (3, 14)

if PY_3_14_PLUS:
    # pylint: disable=import-error
    import annotationlib

    def _get_annotations(cls: type) -> dict[str, Any]:
        return annotationlib.get_annotations(
            cls, format=annotationlib.Format.FORWARDREF
        )

else:

    def _get_annotations(cls: type) -> dict[str, Any]:
        return cls.__annotations__
