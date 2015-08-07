#! /usr/bin/env python

try:
  import pyver
except ImportError:
  import pip
  pip.main (['install', 'pyver'])
  import pyver # pylint: disable=W0611

from setuptools import setup, find_packages
import glob

__version__, __version_info__ = pyver.get_version (pkg = "qworkerd",
                                                   public = True)

setup (
    name = "qworkerd",
    version = __version__,
    description = "Celery disk-job based worker",
    long_description = file ("README.rst").read (),
    classifiers = [],
    keywords = "celery, worker, disk job",
    author = "J C Lawrence",
    author_email = "claw@kanga.nu",
    url = "http://kanga.nu/~claw/",
    license = "GPL v3.0",
    packages = find_packages (exclude = ["tests"]),
    package_data = {"qworkerd": ["_cfgtool/qworkerd",
                                 "_cfgtool/*.templ",
                                 "_cfgtool/install",],
    },
    data_files = [
        ("/etc/cfgtool/module.d/", ["qworkerd/_cfgtool/qworkerd",]),
        ("/etc/qworkerd", glob.glob ("qworkerd/_cfgtool/*.templ")),
        ("./bin", ["qworkerd/qworkerd_manage.py"]),
    ],
    zip_safe = False,
    install_requires = [line.strip ()
                        for line in file ("requirements.txt").readlines ()],
    entry_points = {
        "console_scripts": [
        ],
    },
)
