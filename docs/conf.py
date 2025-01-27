# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
sys.path.insert(0, os.path.abspath(".."))

from galois import __version__

import numpy


# -- Project information -----------------------------------------------------

project = "galois"
copyright = "2020-2022, Matt Hostetter"
author = "Matt Hostetter"
version = __version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "sphinxcontrib.details.directive",
    "recommonmark",
    "sphinx_immaterial",
    "IPython.sphinxext.ipython_console_highlighting",
    "IPython.sphinxext.ipython_directive"
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = [".rst", ".md", ".ipynb"]

# Tell sphinx that ReadTheDocs will create an index.rst file as the main file,
# not the default of contents.rst.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".ipynb_checkpoints"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_immaterial"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = [
    "extra.css",
]

# Sets the default role of `content` to :samp:`content`, which mimics inline literals ``content```
default_role = "samp"

html_title = "galois"
html_favicon = "../logo/galois-favicon-color.png"
html_logo = "../logo/galois-favicon-white.png"

# material theme options (see theme.conf for more information)
html_theme_options = {
    "icon": {
        "repo": "fontawesome/brands/github",
    },
    "site_url": "https://galois.readthedocs.io/",
    "repo_url": "https://github.com/mhostetter/galois",
    "repo_name": "mhostetter/galois",
    "repo_type": "github",
    "edit_uri": "",
    "google_analytics": ["G-4FW9NCNFZH", "auto"],
    "globaltoc_collapse": False,
    "features": [
        # "navigation.expand",
        "navigation.tabs",
        # "toc.integrate",
        # "navigation.sections",
        # "navigation.instant",
        # "header.autohide",
        "navigation.top",
        "navigation.tracking",
    ],
    "palette": [
        {
            "media": "(prefers-color-scheme: light)",
            "scheme": "default",
            "accent": "deep-orange",
            "toggle": {
                "icon": "material/weather-sunny",
                "name": "Switch to dark mode",
            },
        },
        {
            "media": "(prefers-color-scheme: dark)",
            "scheme": "slate",
            "accent": "deep-orange",
            "toggle": {
                "icon": "material/weather-night",
                "name": "Switch to light mode",
            },
        },
    ],
    # "font": {
    #     "code": "Ubuntu Mono"
    # },
    # "version_dropdown": True,
    # "version_info": [
    #     {
    #         "version": "https://sphinx-immaterial.rtfd.io",
    #         "title": "ReadTheDocs",
    #         "aliases": []
    #     },
    #     {
    #         "version": "https://jbms.github.io/sphinx-immaterial",
    #         "title": "Github Pages",
    #         "aliases": []
    #     },
    # ],
}

html_last_updated_fmt = ""
html_use_index = True
html_domain_indices = True

# -- Extension configuration -------------------------------------------------

# Create hyperlinks to other documentation
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "numba": ("https://numba.pydata.org/numba-doc/latest/", None)
}

# pygments_style = "solarized-light"

autodoc_default_options = {
    "imported-members": True,
    "members": True,
    "undoc-members": True,
    "special-members": "__call__, __len__",
    "member-order": "groupwise",
    "inherited-members": "ndarray"  # Inherit from all classes except np.ndarray
}
autodoc_typehints = "none"

autosummary_generate = True
autosummary_generate_overwrite = True
autosummary_imported_members = True

ipython_execlines = ["import math", "import numpy as np", "import galois"]


# -- Functions and setup -----------------------------------------------------

def skip_member(app, what, name, obj, skip, options):
    """
    Instruct autosummary to skip members that are inherited from np.ndarray
    """
    if skip:
        # Continue skipping things sphinx already wants to skip
        return skip

    if "special-members" in options and name in options["special-members"]:
        # Don"t skip members in "special-members"
        return False

    if name[0] == "_":
        # For some reason we need to tell sphinx to hide private members
        return True

    if hasattr(obj, "__objclass__"):
        # This is a numpy method, don't include docs
        return True
    elif hasattr(obj, "__qualname__") and hasattr(numpy.ndarray, name):
        # This is a numpy method that was overridden in one of our ndarray subclasses. Also don't include
        # these docs.
        return True

    return skip


def setup(app):
    app.connect("autodoc-skip-member", skip_member)
