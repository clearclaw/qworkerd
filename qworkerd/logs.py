#! /usr/bin/env python

import logtool, logging, logging.config

@logtool.log_call
def logging_loader (thing):
  if isinstance (thing, str):
    logging.config.fileConfig (thing, disable_existing_loggers = False)
  elif isinstance (thing, dict):
    logging.config.dictConfig (thing)
  else:
    raise ValueError ("Unknown logging setting type.")
