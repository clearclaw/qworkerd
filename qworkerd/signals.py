#! /usr/bin/env python

import logging, logging.config, logtool
from celery import Celery
from celery.signals import celeryd_after_setup, setup_logging

LOG = logging.getLogger (__name__)
DEFAULT_LOGCONF = "/etc/qworkerd/logging.conf"

@setup_logging.connect
@logtool.log_call
def setup_logging_handler (**kwargs): # pylint: disable=W0613
  logging.config.fileConfig (DEFAULT_LOGCONF,
                             disable_existing_loggers = False)

@celeryd_after_setup.connect
def setup_direct_queue (sender, instance, **kwargs):
  # sender is the nodename of the worker
  queue_name = '{0}.dq'.format (sender)
  instance.app.amqp.queues.select_add (queue_name)
