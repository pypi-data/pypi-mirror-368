import os
from datetime import datetime

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "autoapi.extension",
    "sphinx_changelog",
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
]

# Add any paths that contain templates here, relative to this directory.
# templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied

# The suffix(es) of source filenames.
# You can specify multiple suffixes as a list of strings:
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The reST default role (used for this markup: `text`) to use for all
# documents. Set to the "smart" one.
default_role = "obj"

# Disable having a separate return type row
napoleon_use_rtype = False

# Disable google style docstrings
napoleon_google_docstring = False

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".

# Render inheritance diagrams in SVG
graphviz_output_format = "svg"
graphviz_dot_args = [
    "-Nfontsize=10",
    "-Nfontname=Helvetica Neue, Helvetica, Arial, sans-serif",
    "-Efontsize=10",
    "-Efontname=Helvetica Neue, Helvetica, Arial, sans-serif",
    "-Gfontsize=10",
    "-Gfontname=Helvetica Neue, Helvetica, Arial, sans-serif",
]
# Use a top-to-bottom orientation for the diagrams
inheritance_graph_attrs = dict(
    rankdir="TB",
    fontsize=12,
    size='"16.0, 20.0"',
)

# -- Project information -------------------------------------------------------
author = "NSO / AURA"
copyright = "{}, {}".format(datetime.now().year, author)

# Suppress warnings about overriding directives as we overload some of the
# doctest extensions.
suppress_warnings = [
    "app.add_directive",
]

# Inject the canonical URL from the RTD context if present
html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL", "")
