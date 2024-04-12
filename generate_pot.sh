#!/usr/bin/env sh
#
# SPDX-FileCopyrightText: 2024 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Set VIRTUAL_ENV if one does not exist.
if [ -z "${VIRTUAL_ENV}" ]; then
    VIRTUAL_ENV=$(poetry env info --path)
fi

# Get all the translation strings from the source.
xgettext --add-comments --from-code=utf-8 --output=po/protokolo.pot src/**/*.py
xgettext --add-comments --output=po/click.pot "${VIRTUAL_ENV}"/lib/python*/*-packages/click/**.py

# Put everything in protokolo.pot.
msgcat --output=po/protokolo.pot po/protokolo.pot po/click.pot
# Update the .po files.
for name in po/*.po
do
    msgmerge --output="${name}" "${name}" po/protokolo.pot;
done
