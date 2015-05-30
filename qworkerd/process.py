#! /usr/bin/env python

import contextlib, logging, logtool, psutil, retryp
import signal, subprocess, time
from qworkerd.chdircontext import chdir

LOG = logging.getLogger (__name__)

@retryp.retryp (expose_last_exc = True, log_faults = True)
@logtool.log_call
def kill_all_children ():
  for sig in [signal.SIGTERM, signal.SIGKILL,]:
    for child in psutil.Process ().get_children (recursive = True):
      try:
        exe = None
        name = None
        if child.is_running ():
          exe = child.exe ()
          name = child.name ()
          child.send_signal (sig)
      except:
        LOG.error ("Problem %s child: %s(%s) - %s",
                   ("SIGTERM" if sig == signal.SIGTERM else "SIGKILL"),
                   name, child.pid, exe)
        raise
  pcount = len (psutil.Process ().get_children (recursive = True))
  if pcount == 0:
    return
  time.sleep (15) # Wait to quiesce if there's processes left
  raise Exception ("Child processes still won't die: %s" % pcount)

@contextlib.contextmanager
@logtool.log_call
def process (exe, proc_args = [], # pylint: disable=W0102
             cwd = None, pidfile = None):
  try:
    with chdir (dname = cwd) as proc_dir:
      with subprocess.Popen (
          [exe] + proc_args, cwd = proc_dir, shell = True,
          universal_newlines = True,) as proc:
        if pidfile:
          with open (pidfile, "w") as f:
            f.write ("%d\n" % proc.pid)
      yield proc
  finally:
    time.sleep (15) # Wait to quiesce
    kill_all_children ()
