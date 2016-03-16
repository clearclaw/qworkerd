#! /usr/bin/env python

import django, logging, logtool, os, psutil
import raven, raven.transport.http, socket, sys
from celery import Celery
from celery.exceptions import Retry
from celery.signals import setup_logging
from django.conf import settings

LOG = logging.getLogger (__name__)
DEFAULT_LOGCONF = "/etc/qworkerd/logging.conf"

django.setup ()
os.environ.setdefault ("DJANGO_SETTINGS_MODULE", "qworkerd.settings")
app = Celery ("qworkerd")
app.config_from_object ("django.conf:settings")
app.autodiscover_tasks (lambda: settings.INSTALLED_APPS)
app.set_current ()

@setup_logging.connect
@logtool.log_call
def setup_logging_handler (**kwargs): # pylint: disable=W0613
  logging.config.fileConfig (DEFAULT_LOGCONF,
                             disable_existing_loggers = False)

@logtool.log_call
def sentry_exception (e, request, message = None):
  """Yes, this eats exceptions"""
  sentry_tags = {"component": settings.APPLICATION_NAME}
  try:
    sentry = raven.Client (settings.RAVEN_CONFIG["dsn"],
                           auto_log_stacks = True,
                           release = "%s: %s" % (settings.APPLICATION_NAME,
                                                 settings.APPLICATION_VERSION),
                           transport = raven.transport.http.HTTPTransport)
    logtool.log_fault (e, message = message)
    data = {
      "job": request,
    }
    if message:
      data["message"] = message
    sentry.extra_context (data)
    if e is not None:
      einfo = sys.exc_info ()
      rc = sentry.captureException (einfo, **sentry_tags)
      del einfo
    else:
      rc = sentry.capture (**sentry_tags)
    LOG.error ("Sentry filed: %s", rc)
  except Exception as ee:
    logtool.log_fault (ee, message = "FAULT: Problem logging exception.")

@logtool.log_call
def retry_handler (task, e, fail_handler = None):
  try:
    LOG.info ("Retrying.  Attempt: #%s", task.request.retries)
    raise task.retry (exc = e, max_retries = settings.FAIL_RETRYCOUNT,
                      countdown = (settings.FAIL_WAITTIME
                                   * (task.request.retries + 1)))
  except Retry: # Why yes, we're retrying
    raise
  except: # pylint: disable=W0702
    LOG.error ("Max retries reached: %s  GIVING UP!", task.request.retries)
    if fail_handler:
      fail_handler ()
    sentry_exception (e, task.request)
    raise

@app.task
@logtool.log_call
def status ():
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
    "process": {},
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
