#! /bin/bash

export DJANGO_SETTINGS_MODULE=qworkerd.settings
celery -A qworkerd.main worker -c 1 -l debug
