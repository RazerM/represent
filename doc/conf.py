"""Configuration file for the Sphinx documentation builder.

This file only contains a selection of the most common options. For a full
list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
import re
from importlib.metadata import distribution

from parver import Version

# -- Project information -----------------------------------------------------

dist = distribution("Represent")

_release = Version.parse(dist.version)
# Truncate release to x.y
_version = Version(release=_release.release[:2]).truncate(min_length=3)

author_email = dist.metadata["Author-email"]
author, _ = re.match(r"(.*) <(.*)>", author_email).groups()

project = "Represent"
copyright = f"2023, {author}"

# The full version, including alpha/beta/rc tags
release = str(_release)
# The short X.Y.Z version matching the git tags
version = str(_version)

html_title = f"{project} {release}"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

pygments_style = "tango"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# -- Extension configuration -------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "ipython": ("https://ipython.readthedocs.io/en/stable/", None),
    "rich": ("https://rich.readthedocs.io/en/stable/", None),
}

autodoc_member_order = "bysource"
