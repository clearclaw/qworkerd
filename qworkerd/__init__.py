#! /usr/bin/env python

from __future__ import absolute_import
from ._version import get_versions
__version__ = get_versions ()['version']
__version_info__ = get_versions ()
del get_versions

from . import main, tasks
