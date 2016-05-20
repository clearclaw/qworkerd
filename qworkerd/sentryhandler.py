#! /usr/bin/env python

from __future__ import absolute_import
import logging, logtool
import raven, raven.transport.http, sys
from . import settings

LOG = logging.getLogger (__name__)

@logtool.log_call
def _settings_value (sets, key, default):
  if sets is not None and hasattr (sets, key):
    return getattr (sets, key)
  return getattr (settings, key, default)

@logtool.log_call
def sentry_handler (e, task, message = None, local_settings = None):
  """Yes, this eats exceptions"""
  try:
    app_name = _settings_value (local_settings, "APPLICATION_NAME",
                                settings.APPLICATION_NAME)
    app_ver = _settings_value (
      local_settings, "APPLICATION_VERSION",
      settings.APPLICATION_VERSION if app_name == settings.APPLICATION_NAME
      else "unknown")
    app_dsn = _settings_value (
      local_settings, "SENTRY_DSN",
      settings.RAVEN_CONFIG["dsn"]) # pylint: disable=no-member
    app_tags = {"component": app_name,
                   "version": app_ver}
    # Localise the Sentry for the plugin
    sentry = raven.Client (app_dsn,
                           auto_log_stacks = True,
                           release = "%s: %s" % (app_name, app_ver),
                           transport = raven.transport.http.HTTPTransport)
    logtool.log_fault (e, message = message, level = logging.INFO)
    data = {
      "tags": app_tags,
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
        "reply_to": task.request.reply_to,
        "retries": task.request.retries,
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
    rc = sentry.captureException (einfo, **app_tags)
    del einfo
    LOG.error ("Sentry filed: %s", rc)
  except Exception as ee:
    logtool.log_fault (ee, message = "FAULT: Problem logging exception.",
                       level = logging.INFO)
