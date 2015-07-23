#! /usr/bin/env python

import logging, logtool, os, psutil, socket
from celery import Celery
from celery.signals import celeryd_after_setup, setup_logging
from django.conf import settings

LOG = logging.getLogger (__name__)
DEFAULT_LOGCONF = "/etc/qworkerd/logging.conf"

os.environ.setdefault ("DJANGO_SETTINGS_MODULE", "qworkerd.settings")
app = Celery ("qworkerd")
app.config_from_object ("django.conf:settings")
app.autodiscover_tasks (lambda: settings.INSTALLED_APPS)
app.set_current ()

@setup_logging.connect
#@logtool.log_call
def setup_logging_handler (**kwargs): # pylint: disable=W0613
  logging.config.fileConfig (DEFAULT_LOGCONF,
                             disable_existing_loggers = False)

# Replaced by config setting?                             
#@celeryd_after_setup.connect
## @logtool.log_call
#def setup_direct_queue (sender, instance, **kwargs): # pylint: disable=W0613
#  # sender is the nodename of the worker
#  queue_name = '{0}.dq'.format (sender)
#  instance.app.amqp.queues.select_add (queue_name)

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
  for proc in psutil.process_iter ():
    if proc.username == settings.UNIX_USER:
      rc["process"]["proc.pid"] = {
        "name": proc.name,
        "exe": proc.exe,
        "cmdline": proc.cmdline,
        "create_time": proc.create_time (),
        "since":  logtool.time_str (proc.create_time (), slug = True),
        "status": proc.status (),
        "cpu.times": proc.cpu_times (),
        "cpu.percent": proc.cpu_percent (),
        "memory.info": proc.memory_info_ex (),
        "percent": proc.memory_percent (),
      }
  return rc

if __name__ == "__main__":
  app.start()
