# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: CC-BY-SA-4.0 OR GPL-3.0-or-later

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Protokolo"
copyright = "2023, Carmen Bianca BAKKER"
author = "Carmen Bianca BAKKER"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinxcontrib.apidoc",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Extensions configuration ------------------------------------------------

apidoc_module_dir = "../src/protokolo"
# apidoc_output_dir = "api"
# apidoc_excluded_paths = []
apidoc_separate_modules = True

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]

man_pages = [
    (
        "man/protokolo",
        "protokolo",
        "A change log generator",
        "Carmen Bianca BAKKER",
        1,
    ),
    (
        "man/protokolo-compile",
        "protokolo-compile",
        "Compile the contents of the change log directory into a change log file.",
        "Carmen Bianca BAKKER",
        1,
    ),
    (
        "man/protokolo-init",
        "protokolo-init",
        "Set up your project for use with protokolo",
        "Carmen Bianca BAKKER",
        1,
    ),
]
