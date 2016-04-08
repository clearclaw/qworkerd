#! /usr/bin/env python

from setuptools import setup, find_packages
import glob, versioneer

setup (
    name = "qworkerd",
    version = versioneer.get_version (),
    description = "Celery based worker (default/pluggable)",
    long_description = file ("README.rst").read (),
    cmdclass = versioneer.get_cmdclass (),
    classifiers = [
      "Development Status :: 4 - Beta",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: "
      + "GNU Lesser General Public License v3 or later (LGPLv3+)",
      "Topic :: Utilities",
    ],
    keywords = "celery, worker",
    author = "J C Lawrence",
    author_email = "claw@kanga.nu",
    url = "https://github.com/clearclaw/qworkerd",
    license = "LGPL v3.0",
    packages = find_packages (exclude = ["tests"]),
    package_data = {"qworkerd": ["_cfgtool/qworkerd",
                                 "_cfgtool/*.templ",
                                 "_cfgtool/install",],
    },
    data_files = [
        ("/etc/cfgtool/module.d/", ["qworkerd/_cfgtool/qworkerd",]),
        ("/etc/qworkerd", glob.glob ("qworkerd/_cfgtool/*.templ")),
    ],
    zip_safe = False,
    install_requires = [line.strip ()
                        for line in file ("requirements.txt").readlines ()],
    entry_points = {
        "console_scripts": [
          "qworkerd_manage = qworkerd.manage:main"
        ],
    },
)
