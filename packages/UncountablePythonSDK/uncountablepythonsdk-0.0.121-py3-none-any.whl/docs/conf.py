# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import datetime

project = "Uncountable SDK"
copyright = f"{datetime.datetime.now(tz=datetime.UTC).date().year}, Uncountable Inc"
author = "Uncountable Inc"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "autoapi.extension",
    "myst_parser",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx_favicon",
]
myst_enable_extensions = ["fieldlist", "deflist"]

autoapi_dirs = ["../uncountable"]
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]
autoapi_ignore = ["*integration*"]
autodoc_typehints = "description"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_title = "Python SDK"
html_static_path = ["static"]
html_logo = "static/logo_blue.png"

favicons = [
    "favicons/android-chrome-192x192.png",
    "favicons/android-chrome-512x512.png",
    "favicons/apple-touch-icon.png",
    "favicons/favicon-16x16.png",
    "favicons/favicon-32x32.png",
    "favicons/mstile-150x150.png",
    "favicons/safari-pinned-tab.svg",
]
