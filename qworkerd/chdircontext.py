#! /usr/bin/env python

import contextlib, logging, logtool, os

LOG = logging.getLogger (__name__)

@contextlib.contextmanager
@logtool.log_call
def chdir (dname = None):
  cwd = os.getcwd ()
  try:
    if dname is not None:
      os.chdir (dname)
    yield dname
  finally:
    os.chdir (cwd)
