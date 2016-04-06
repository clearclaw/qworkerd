#! /usr/bin/env python

from celery import Task

class QWTask (Task): # pylint: disable=abstract-method

  #: If :const:`True` the task is an abstract base class.
  #: Note: Also set this in derived clases?
  abstract = True

  #: The name of a serializer that are registered with
  #: :mod:kombu.serialization.registry.  Default is 'pickle'.
  serializer = "json"

  #: Maximum number of retries before giving up.  If set to :const:`None`,
  #: it will **never** stop retrying.
  max_retries = 3

  #: Default time to wait and the base multiplier for exponential
  #: backoff on retries.
  default_retry_period = 5

  #: Default time in seconds before a retry of the task should be
  #: executed.  3 minutes by default.
  # default_retry_delay = 3 * 60
  @property
  def default_retry_delay (self):
    return self.default_retry_period * (self.request.retries + 1)

  #: Hard time limit.
  #: Defaults to the :setting:`task_time_limit` setting.
  time_limit = None

  #: Soft time limit.
  #: Defaults to the :setting:`task_soft_time_limit` setting.
  soft_time_limit = None

  #: If enabled the task will report its status as 'started' when the task
  #: is executed by a worker.  Disabled by default as the normal behaviour
  #: is to not report that level of granularity.  Tasks are either pending,
  #: finished, or waiting to be retried.
  #:
  #: Having a 'started' status can be useful for when there are long
  #: running tasks and there is a need to report which task is currently
  #: running.
  #:
  #: The application default can be overridden using the
  #: :setting:`task_track_started` setting.
  track_started = True

  #: Even if :attr:`acks_late` is enabled, the worker will
  #: acknowledge tasks when the worker process executing them abrubtly
  #: exits or is signaled (e.g. :sig:`KILL`/:sig:`INT`, etc).
  #:
  #: Setting this to true allows the message to be requeued instead,
  #: so that the task will execute again by the same worker, or another
  #: worker.
  #:
  #: Warning: Enabling this can cause message loops; make sure you know
  #: what you're doing.
  reject_on_worker_lost = True
