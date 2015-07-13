#! /usr/bin/env python

from setuptools import setup, find_packages
import pyver

__version__, __version_info__ = pyver.get_version (pkg = "qworkerd")

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
    include_package_data = True,
    package_data = {"": ["_cfgtool/*.templ", "_cfgtool/install"],},
    zip_safe = False,
    install_requires = [line.strip ()
                        for line in file ("requirements.txt").readlines ()],
    entry_points = {
        "console_scripts": [
        ],
    },
)
