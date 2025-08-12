# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import pathlib
import sys
# print(pathlib.Path(__file__).parents[2])
fld = pathlib.Path(__file__).parents[2].resolve().as_posix()
sys.path.insert(0,fld)

project = 'MulDataFrame'
copyright = '2024, Qiaonan Duan and Fei Wang'
author = 'Qiaonan Duan, Fei Wang'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx_favicon',
    # 'sphinx_sitemap'
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_title = '<img style="width:50px; margin-right:0.5em" src="https://frlender.github.io/muldataframe-doc/_static/android-chrome-192x192.png">MulDataFrame'
html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']

# favicons = [
#     "favicon-16x16.png",
#     "favicon-32x32.png",
#     "favicon.ico",
# ]

favicons = [
    # "https://frlender.github.io/muldataframe-doc/_static/favicon-16x16.png",
    # "https://frlender.github.io/muldataframe-doc/_static/favicon-32x32.png",
    "https://frlender.github.io/muldataframe-doc/_static/favicon.ico?",
]