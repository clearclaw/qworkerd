#! /usr/bin/env python

import logging, logtool, os
from celery import Celery
from celery.signals import celeryd_after_setup, setup_logging
from django.conf import settings

LOG = logging.getLogger (__name__)
DEFAULT_LOGCONF = "/etc/qworkerd/logging.conf"

os.environ.setdefault ("DJANGO_SETTINGS_MODULE", "qworkerd.settings")
app = Celery ("qworkerd", include = ["qworkerd.tasks",])
app.config_from_object ("django.conf:settings")
app.autodiscover_tasks (lambda: settings.INSTALLED_APPS)
app.set_current ()

@setup_logging.connect
#@logtool.log_call
def setup_logging_handler (**kwargs): # pylint: disable=W0613
  logging.config.fileConfig (DEFAULT_LOGCONF,
                             disable_existing_loggers = False)

@celeryd_after_setup.connect
# @logtool.log_call
def setup_direct_queue (sender, instance, **kwargs): # pylint: disable=W0613
  # sender is the nodename of the worker
  queue_name = '{0}.dq'.format (sender)
  instance.app.amqp.queues.select_add (queue_name)

if __name__ == "__main__":
  app.start()
