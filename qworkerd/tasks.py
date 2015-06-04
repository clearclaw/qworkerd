#! /usr/bin/env python

import datetime, logging, logtool, psutil, socket
from django.conf import settings
from celery import current_app

LOG = logging.getLogger (__name__)

@logtool.log_call
def nice_date (ut):
  return datetime.datetime.fromtimestamp (
    float (ut)).strftime ("%Y-%m-%d %H:%M:%S")

@logtool.log_call
@current_app.task
def host_status ():
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
      "since": nice_date (psutil.boot_time ()),
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
        "since": (nice_date (proc.create_time ())),
        "status": proc.status (),
        "cpu.times": proc.cpu_times (),
        "cpu.percent": proc.cpu_percent (),
        "memory.info": proc.memory_info_ex (),
        "percent": proc.memory_percent (),
      }
  return rc
