#! /usr/bin/env python

from __future__ import absolute_import
import logging, logtool
from celery.exceptions import Retry

LOG = logging.getLogger (__name__)

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
    raise
