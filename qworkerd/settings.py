#! /usr/bin/env python

import logging, logtool, sys

LOG = logging.getLogger (__name__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname (os.path.dirname (__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "McmillanCompressorsBennyCalifChromingFoundersDisassociates"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Application definition
INSTALLED_APPS = (
  "raven.contrib.django.raven_compat",
  "rest_framework",
  "djcelery",
  "qworkerd",
)
MIDDLEWARE_CLASSES = ()

# It's not always possible to detect connection loss in a timely
# manner using TCP/IP alone, so AMQP defines something called heartbeats
# that's is used both by the client and the broker to detect if a
# connection was closed.
BROKER_HEARTBEAT = 10

# Maximum number of tasks a pool worker process can execute before
# it's replaced with a new one. Default is no limit.
CELERYD_MAX_TASKS_PER_CHILD = 5

# Let"s use SQL for the results?  We need SQL that isn't Django specific.
# CELERY_RESULT_BACKEND = "db+mysql://task:task@localhost/task"
# CELERY_RESULT_BACKEND = "djcelery.backends.database:DatabaseBackend"

# django-celery also ships with a scheduler that stores the schedule
# in the Django database:
#CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json",]  # Ignore other content

# Need to investigate failure handling.
#def my_on_failure(self, exc, task_id, args, kwargs, einfo):
#    print("Oh no! Task failed: {0!r}".format(exc))
#CELERY_ANNOTATIONS = {"*": {"on_failure": my_on_failure}}

# Number of jobs for the worker to take off the queue at a time.
CELERYD_PREFETCH_MULTIPLIER = 1

# If True the task will report its status as "started" when the task
# is executed by a worker. The default value is False as the normal
# behaviour is to not report that level of granularity. Tasks are either
# pending, finished, or waiting to be retried. Having a "started" state
# can be useful for when there are long running tasks and there is a
# need to report which task is currently running.
CELERY_TRACK_STARTED = True

# Late ack means the task messages will be acknowledged after the task
# has been executed, not just before, which is the default behavior.
CELERY_ACKS_LATE = True

# Keep results forever
CELERY_TASK_RESULT_EXPIRES = 0  # Never

# If set to True, result messages will be persistent. This means the
# messages will not be lost after a broker restart. The default is for
# the results to be transient.
# CELERY_RESULT_PERSISTENT = True

# Send events so the worker can be monitored by tools like celerymon.
CELERY_SEND_EVENTS = True

# If enabled, a task-sent event will be sent for every task so tasks
# can be tracked before they are consumed by a worker.
CELERY_SEND_TASK_SENT_EVENT = True

# Enables error emails.
CELERY_SEND_TASK_ERROR_EMAILS = False

# Number of simultaneous jobs to run on the worker
CELERYD_CONCURRENCY = 1

# Task hard time limit in seconds. The worker processing the task will
# be killed and replaced with a new one when this is exceeded.
CELERYD_TASK_TIME_LIMIT = 13 * 60 * 60

# Task soft time limit in seconds.
# The SoftTimeLimitExceeded exception will be raised when this is
# exceeded. The task can catch this to e.g. clean up before the hard
# time limit comes.
# http://celery.readthedocs.org/en/latest/configuration.html#celeryd-task-soft-time-limit
CELERYD_TASK_SOFT_TIME_LIMIT = 12 * 60 * 60

## # This setting can be used to rewrite any task attribute from the
## # configuration. The setting can be a dict, or a list of annotation
## # objects that filter for tasks and return a map of attributes to
## # change.
##
## import logging, logtool
##
## @logtool.log_call (log_level = logging.ERROR)
## def mp_on_failure (self, exc, task_id, args, kwargs, einfo):
##   LOG = logging.getLogger (__name__)
##   logtool.log_fault (exc)
##
## CELERY_ANNOTATIONS = {"*": {"on_failure": mp_on_failure}}

# A sequence of modules to import when the worker starts.
CELERY_IMPORTS = ("qeventlog.qetask", "qworkerd.tasks",)

# Exact same semantics as CELERY_IMPORTS, but can be used as a means
# to have different import categories.
CELERY_INCLUDE = []

# https://github.com/ssaw/celery-statsd
STATSD_HOST = "127.0.0.1"
STATSD_PORT = 8125
CELERYD_STATS_PREFIX = "qworkerd."

LOGGING = "/etc/qworkerd/logging.conf"
LOGGING_CONFIG = "qworkerd.logs.logging_loader"

EXTERNAL_CONFIG = "/etc/qworkerd/qworkerd.conf"
execfile (EXTERNAL_CONFIG)

DESIRED_VARIABLES = [
  "SECRET_KEY",
  "LOGGING",
  "CELERYD_CONCURRENCY",
  "CELERYD_TASK_TIME_LIMIT",
  "CELERYD_TASK_SOFT_TIME_LIMIT",
]
REQUIRED_VARIABLES = [
  "RAVEN_CONFIG",
  "BROKER_URL",
#  "CELERY_RESULT_BACKEND",
  "CELERY_INCLUDE",
]

@logtool.log_call
def check_vars (wanted, provided):
  return [var for var in wanted if var not in provided]

missing = check_vars (DESIRED_VARIABLES, vars ())
if missing:
  print >> sys.stderr, "Missing desired configurations: %s" % missing
missing = check_vars (REQUIRED_VARIABLES, vars ())
if missing:
  print >> sys.stderr, "Missing required configurations: %s" % missing
  sys.exit ()