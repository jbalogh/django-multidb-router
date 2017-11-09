from __future__ import unicode_literals
import sys
import os

sys.path.append(os.path.abspath('..'))

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

extensions = ['sphinx.ext.autodoc']

# General information about the project.
project = 'multidb-router'
copyright = '2015, The Zamboni Collective'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '0.7'
# The full version, including alpha/beta/rc tags.
release = '0.7.0'

# List of directories, relative to source directory, that shouldn't be searched
# for source files.
exclude_trees = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
# pygments_style = 'sphinx'
