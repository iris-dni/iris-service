# Shared Source Software
# Copyright (c) 2015, Lovely Systems GmbH

# -*- coding: utf-8 -*-

import os

# inject the VERSION constant used below
# This can be used because the build script updates the version number before
# building the RPM.
here = os.path.dirname(__file__)
project_root = os.path.dirname(here)

VERSION = '?'
execfile(os.path.join(project_root, 'src/iris/service/__init__.py'))
docs_version = VERSION

pyramid_conf = os.path.join(project_root, 'etc', 'development.ini')

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

nitpicky = True

extensions = ['sphinxcontrib.plantuml',
              'sphinxcontrib.httpdomain',
              'sphinx.ext.doctest']

plantuml = ('java'
            ' -Djava.awt.headless=true'
            ' -jar ./plantuml.jar'
           )

# load doctest extension to be able to setup testdata in the documentation that
# is hidden in the generated html (by using .. doctest:: :hide:)
extensions.append('sphinx.ext.doctest')

# General information about the project.
project = u'IRIS'
from datetime import date
copyright = u'{year}, Lovely Systems GmbH'.format(year=date.today().year)

version = release = docs_version
exclude_patterns = ['service.egg-info', 'parts', 'checkouts']

import sphinx_rtd_theme
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
