#! /usr/bin/env python

import itertools, logging, logtool, os
from path import Path
from jsondict import JsonDict

LOG = logging.getLogger (__name__)

class TaskContext (object):

  @logtool.log_call
  def __init__ (self, task, settings, context, job):
    self.task = task
    self.settings = settings
    self.context = context
    self.job = job
    self.uuid = context.id
    self.work_dir = Path (self.settings.WORKING_DIRECTORY)
    self.task_dir = self.work_dir / self.uuid

  @logtool.log_call
  def space_empty (self, d):
    # Can't use glob due to dotfiles
    for entry in d.files ():
      entry.remove ()
    for entry in d.dirs ():
      entry.rmtree ()

  @logtool.log_call
  def workspace_empty (self):
    if not self.settings.NUKE_WORKING_DIRECTORY:
      LOG.debug ("Workdir nuke disabled.")
      return
    self.space_empty (self.work_dir)

  @logtool.log_call
  def workspace_check (self):
    stats = os.statvfs (self.work_dir)
    if stats.f_bavail < int (self.settings.JOB_MINIMUM_FREE_DISK_BLOCKS):
      msg = ("Not enough Free disk in work_dir: %d vs required %s"
             % (stats.f_bavail,
                self.settings.JOB_MINIMUM_FREE_DISK_BLOCKS))
      LOG.error (msg)
      raise ValueError (msg)

  @logtool.log_call
  def workspace_create (self):
    self.task_dir.makedirs_p ()
    self.space_empty (self.task_dir)
    for d in ["data", "result", "report"]:
      (self.task_dir / d).makedirs_p ()
    JsonDict (self.task_dir / "report" / "job.json", self.job)
    JsonDict (self.task_dir / "report" / "request.json", self.context)

  @logtool.log_call
  def __enter__ (self):
    self.workspace_empty ()
    self.workspace_check ()
    self.workspace_create ()
    return self.task_dir

  @logtool.log_call
  def __exit__ (self, typ, value, tb):
    if not Path (self.settings.JOB_NOCLEAN_FILE).isfile ():
      self.workspace_empty ()
