#! /bin/bash

export DJANGO_SETTINGS_MODULE=qworkerd.settings
celery -A qworkerd.main worker -l debug
