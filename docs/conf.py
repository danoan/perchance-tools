# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# Add the package source to the sys.path
import sphinx_rtd_theme
from importlib import metadata
import pathlib
import sys

source_folder = (
    pathlib.Path(__file__).parents[1].joinpath("src/danoan").resolve().as_posix()
)
sys.path.insert(0, source_folder)

# Tell sphinx the package version

PACKAGE_VERSION = metadata.version("perchance-tools")
version = release = PACKAGE_VERSION

# Import read the docs theme

project = "perchance-tools"
copyright = "2024, Daniel Martins Antunes"
author = "Daniel Martins Antunes"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # Collect docstrings
    "sphinx.ext.autodoc.typehints",  # Use typehints
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",  # NumPy and Google docstring format
    "sphinx.ext.viewcode",  # Source code link at function, class, module documentation
    "sphinx_rtd_theme",  # Read the docs theme,
    "myst_parser",  # Markdown flavour. Allow type-hints constructions.
    "sphinxcontrib.mermaid",  # Mermaid diagrams.
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

autodoc_typehints = "both"

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

html_css_files = ["css/custom.css"]
