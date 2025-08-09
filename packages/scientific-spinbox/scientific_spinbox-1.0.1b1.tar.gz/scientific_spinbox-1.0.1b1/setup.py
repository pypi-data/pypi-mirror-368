# python
# -*- coding: utf-8 -*-

"""Setup module for ScientificSpinbox.

Since: 2019/02/07

Authors:
    - Eduardo Rocha Falvo <dudu.falvo@gmail.com>
    - Daniel C. Pizetta <daniel.pizetta@usp.br>
    - Breno H. Pelegrin S. <breno.pelegrin@usp.br>
"""

import codecs
import logging
import os
import re

from setuptools import setup, find_packages

_logger = logging.getLogger(__name__)

def find_version(*file_paths):
    """Find version in a Python file, searching for the __version__."""
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def read(*parts):
    """Read and return the contents of a file."""
    # intentionally *not* adding an encoding option to open, See:
    # https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, *parts), 'r').read()

_version = find_version("scientific_spinbox", "__init__.py")
_long_description = read('README.rst')

_classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: X11 Applications :: Qt',
    'Environment :: Plugins',
    'Intended Audience :: Science/Research',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    'Natural Language :: English',
    'Operating System :: MacOS',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3',
    'Topic :: Scientific/Engineering',
    'Topic :: Software Development :: User Interfaces',
    'Topic :: Text Editors :: Text Processing',
]

_requirements = [
    "pint",
    "pyqt5",
    "qtpy"
]

_setup_requirements = []

setup(name='scientific-spinbox',
      version=_version,
      description='ScientificSpinbox - A Qt widget to manipulate physical quantities',
      author=['Breno Pelegrin'],
      author_email='brenohqsilva@gmail.com',
      maintainer=['Breno Pelegrin <brenohqsilva@gmail.com>', 'Daniel Cosmo Pizetta <daniel.pizetta@alumni.usp.br>'],
      maintainer_email=['brenohqsilva@gmail.com', 'daniel.pizetta@alumni.usp.br'],
      classifiers=_classifiers,
      long_description=_long_description,
      long_description_content_type='text/x-rst',
      license='LGPLv3',
      license_file='LICENSE.rst',
      packages=find_packages(),
      install_requires=_requirements,
      setup_requires=_setup_requirements,
      project_urls={
          "Homepage": "https://dpizetta.gitlab.io/pqwidget",
          "Documentation": "https://pqwidget.readthedocs.io/",
          "Source": "https://gitlab.com/dpizetta/pqwidget",
          "Issues": "https://gitlab.com/dpizetta/pqwidget/issues"
      }
      )
