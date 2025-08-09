# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.append(os.path.abspath('sphinxext'))
import datetime
from importlib import metadata

# -- Project information -----------------------------------------------------

project = 'Jscatter'
copyright = '2015-'+str(datetime.date.today().year)+', Ralf Biehl'
author = 'Ralf Biehl'

__version__ = metadata.version("jscatter")

# -- General configuration ------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    #'sphinx.ext.imgmath',
    'sphinx.ext.mathjax',
    'sphinx_toolbox.collapse',
    'fulltoc',
    'numpydoc',
    'sphinx.ext.autosectionlabel',
    'sphinx_copybutton',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'
# The master toctree document.
master_doc = 'index'
version = __version__
# The full version, including alpha/beta/rc tags.
release = __version__

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# The name of the Pygments (syntax highlighting) style to use.
# pygments_style = 'sphinx'


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "classic"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the documentation.
# bgr='#ffaf4d'
html_theme_options = {
    "stickysidebar": "True",
    "footerbgcolor": '#FF7A14',
    "sidebarbgcolor": '#FF7A14',
    "relbarbgcolor": '#FF7A14',
    "bgcolor": '#E8E8E8',
    "sidebarlinkcolor": '#606060',
    "linkcolor": '#606060',
    "visitedlinkcolor": '#404040',
    "codebgcolor": '#fff1e6',
    "headbgcolor": '#ffd4b3',
    "globaltoc_maxdepth": 1,
    # "collapsiblesidebar": "True",
}

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []


# A shorter title for the navigation bar.  Default is the same as html_title.
html_short_title = project + ' ' + version

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = None
html_logo = '../../examples/Jscatter1.gif'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = None
html_favicon = '../../examples/Jscatter-32x-32.png'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'
# -- imagemath options      ----------------------------------------------
#imgmath_image_format = 'svg'


# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}
numpydoc_show_class_members = False

# Additional settings RB
autoclass_content = 'init'


rst_prolog = """
.. include:: isotech.txt
"""
