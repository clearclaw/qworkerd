#! /usr/bin/env python

from __future__ import absolute_import
import django, logging, logtool, os, psutil
import raven, raven.contrib.celery, raven.transport.http, socket, sys
from celery import Celery
from celery.exceptions import Retry
from celery.signals import setup_logging
from django.conf import settings
from .qwtask import QWTask

from ._version import get_versions
__version__ = get_versions ()['version']
del get_versions

LOG = logging.getLogger (__name__)
DEFAULT_LOGCONF = "/etc/qworkerd/logging.conf"

django.setup ()
os.environ.setdefault ("DJANGO_SETTINGS_MODULE", "qworkerd.settings")
app = Celery ("qworkerd")
app.config_from_object ("django.conf:settings")
app.autodiscover_tasks (lambda: settings.INSTALLED_APPS)
SENTRY = raven.Client (settings.RAVEN_CONFIG["dsn"],
                       auto_log_stacks = True,
                       release = "%s: %s" % ("qworkerd", __version__),
                       transport = raven.transport.http.HTTPTransport)
app.set_current ()

@setup_logging.connect
@logtool.log_call
def setup_logging_handler (**kwargs): # pylint: disable=W0613
  logging.config.fileConfig (DEFAULT_LOGCONF,
                             disable_existing_loggers = False)
  raven.contrib.celery.register_logger_signal (SENTRY)
  raven.contrib.celery.register_signal (SENTRY)

@logtool.log_call
def _settings_value (sets, key, default):
  if sets is not None and hasattr (sets, key):
    return getattr (sets, key)
  return getattr (settings, key, default)

@logtool.log_call
def sentry_exception (e, task, message = None, local_settings = None):
  """Yes, this eats exceptions"""
  try:
    app_name = _settings_value (local_settings, "APPLICATION_NAME", "qworkerd")
    app_ver = _settings_value (local_settings, "APPLICATION_VERSION",
                               "unknown-version")
    sentry_dsn = _settings_value (local_settings, "SENTRY_DSN",
                                  settings.RAVEN_CONFIG["dsn"])
    sentry_tags = {"component": app_name,
                   "version": app_ver}
    # Localise the Sentry for the plugin
    sentry = raven.Client (sentry_dsn,
                           auto_log_stacks = True,
                           release = "%s: %s" % (app_name, app_ver),
                           transport = raven.transport.http.HTTPTransport)
    logtool.log_fault (e, message = message, level = logging.INFO)
    data = {
      "task": task,
      "request": {
        "args": task.request.args,
        "callbacks": task.request.callbacks,
        "called_directly": task.request.called_directly,
        "correlation_id": task.request.correlation_id,
        "delivery_info": task.request.delivery_info,
        "errbacks": task.request.errbacks,
        "eta": task.request.eta,
        "expires": task.request.expires,
        "headers": task.request.headers,
        "hostname": task.request.hostname,
        "id": task.request.id,
        "is_eager": task.request.is_eager,
        "kwargs": task.request.kwargs,
        "parent_id": task.request.parent_id,
        "reply_to": task.request.reply_to,
        "retries": task.request.retries,
        "root_id": task.request.root_id,
        "task": task.request.task,
        "taskset": task.request.taskset,
        "timelimit": task.request.timelimit,
        "utc": task.request.utc,
      },
    }
    if message:
      data["message"] = message
    sentry.extra_context (data)
    einfo = sys.exc_info ()
    rc = sentry.captureException (einfo, **sentry_tags)
    del einfo
    LOG.error ("Sentry filed: %s", rc)
  except Exception as ee:
    logtool.log_fault (ee, message = "FAULT: Problem logging exception.",
                       level = logging.INFO)

@logtool.log_call
def retry_handler (task, e, fail_handler = None):
  try:
    LOG.info ("Retrying.  Attempt: #%s  Delay: %d",
              task.request.retries, task.default_retry_delay)
    raise task.retry (exc = e)
  except Retry: # Why yes, we're retrying
    raise
  except: # pylint: disable=W0702
    LOG.error ("Max retries reached: %s  GIVING UP!", task.request.retries)
    if fail_handler:
      fail_handler ()
    sentry_exception (e, task)
    raise

@app.task (bind = True, base = QWTask)
@logtool.log_call
def status (self): # pylint: disable=unused-argument
  rc = {
    "hostname": socket.gethostname (),
    "cpu": {
      "count": psutil.cpu_count (),
      "times": psutil.cpu_times (),
      "percent": psutil.cpu_percent (percpu = True),
      },
    "memory": {
      "virtual": psutil.virtual_memory (),
      "swap": psutil.swap_memory (),
      },
    "net": psutil.net_io_counters (),
    "uptime": {
      "ut": psutil.boot_time (),
      "since": logtool.time_str (psutil.boot_time (), slug = True),
      },
    "disk": {},
    }
  for part in psutil.disk_partitions ():
    rc["disk"]["mounts"] = {
      part.mountpoint: psutil.disk_usage (part.mountpoint),
    }
  for disk, io in psutil.disk_io_counters (perdisk = True).items ():
    rc["disk"]["io"] = {
      disk: io
    }
  return rc

if __name__ == "__main__":
  app.start ()
