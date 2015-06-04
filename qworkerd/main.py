#! /usr/bin/env python

import logging, os
from celery import Celery
from django.conf import settings

LOG = logging.getLogger (__name__)

os.environ.setdefault ("DJANGO_SETTINGS_MODULE", "qworkerd.settings")
app = Celery ("qworkerd", include = ["qworkerd.tasks",])
app.config_from_object ("django.conf:settings")
app.autodiscover_tasks (lambda: settings.INSTALLED_APPS)
app.set_current ()

if __name__ == "__main__":
  app.start()
