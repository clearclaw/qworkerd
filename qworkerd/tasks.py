#!/usr/bin/env python

import logging, logtool, os
import qeventlog.qetask # pylint: disable=W0611
from django.conf import settings
from qworkerd.main import app # pylint: disable=W0611
from celery import current_app
from qworkerd.taskcontext import TaskContext
from qworkerd.process import process

LOG = logging.getLogger (__name__)

class MpTaskException (Exception):
  pass

@logtool.log_call
def search_os_path (name, env_path = None, exts = ('',)):
  s_path = env_path or os.environ.get ("PATH", "")
  exts_n = [os.extsep + (ext if not ext.startswith (os.extsep)
                         else ext[len (os.extsep):])
            for ext in exts if ext is not ""]
  if "" in exts:
    exts_n.append ("")
  exts = exts_n
  for d in s_path.split (os.pathsep):
    for ext in exts:
      binpath = os.path.join (d, name) + ext
      if os.path.exists (binpath):
        return os.path.abspath (binpath)
  return None

@logtool.log_call
def get_exebin (exe):
  exebin = search_os_path (exe, exts = (".py", ".sh", "",))
  if exebin:
    return exebin
  msg = "Failed to fined executable for: %s" % exe
  LOG.error (msg)
  raise MpTaskException (msg)

@logtool.log_call
@current_app.task (bind = True)
def do (this, task, **kwargs):
  with TaskContext (settings, this.request, kwargs) as job_dir:
    exebin = get_exebin (task)
    LOG.info ("Start: %s", exebin)
    with process ([exebin,],
                  proc_args = {"shell": True,
                               "universal_newlines": True,
                               "cwd": job_dir},
                  cwd = job_dir,
                  pidfile = job_dir,) as proc:
      rc = proc.wait ()
      LOG.info ("End: %s RC: %s", exebin, rc)
