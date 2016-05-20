#! /usr/bin/env python

from __future__ import absolute_import
import django, logging, logtool, os
import raven, raven.contrib.celery, raven.transport.http
from celery import Celery
from celery.signals import setup_logging

from . import settings

LOG = logging.getLogger (__name__)
DEFAULT_LOGCONF = "/etc/qworkerd/logging.conf"

django.setup ()
os.environ.setdefault ("DJANGO_SETTINGS_MODULE", "qworkerd.settings")
app = Celery ("qworkerd")
app.config_from_object ("django.conf:settings")
app.autodiscover_tasks (lambda: settings.INSTALLED_APPS)
SENTRY = raven.Client (
  settings.RAVEN_CONFIG["dsn"], # pylint: disable=no-member
  auto_log_stacks = True,
  release = "%s: %s" % (settings.APPLICATION_NAME,
                        settings.APPLICATION_VERSION),
  transport = raven.transport.http.HTTPTransport)
app.set_current ()

@setup_logging.connect
@logtool.log_call
def setup_logging_handler (**kwargs): # pylint: disable=W0613
  logging.config.fileConfig (DEFAULT_LOGCONF,
                             disable_existing_loggers = False)
  raven.contrib.celery.register_logger_signal (SENTRY)
  raven.contrib.celery.register_signal (SENTRY)

if __name__ == "__main__":
  app.start ()
