# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Goldy Bot V5'
copyright = '2023, Goldy'
author = 'Goldy'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.todo", 
    "sphinx.ext.viewcode", 
    "sphinx.ext.autodoc",
    "sphinxext.opengraph",
    "sphinx_inline_tabs",
    "myst_parser",
    "sphinx_copybutton"
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
source_suffix = ['.rst', '.md']

# Opengraph Settings
# -------------------
ogp_site_url = "https://goldybot.devgoldy.xyz"
ogp_social_cards = {
    "line_color": "#bf5c00",
    "width": 500
}
ogp_image = "_static/logo.png"


html_theme_options = {
    "dark_css_variables": {
        "color-brand-primary": "orange",
        "color-brand-content": "#ffdfae",
        "color-admonition-background": "#0d0904",
    },

    "light_css_variables": {
        "color-brand-primary": "orange",
        "color-brand-content": "#c95f12",
        "color-admonition-background": "#ffe7ae",
    }
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ['_static']
html_logo = "_static/logo.png"
html_favicon = "_static/logo.png"