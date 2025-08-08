import os
import sys
import logging
from functools import partial
from appPublic.timeUtils import timestampstr
levels={
	"debug":logging.DEBUG,
	"info":logging.INFO,
	"warning":logging.WARNING,
	"error":logging.error,
	"critical":logging.CRITICAL
}
defaultfmt = '%(asctime)s[%(name)s][%(levelname)s][%(filename)s:%(lineno)s]%(message)s'
logfile = -1
logger = None
g_levelname='info'
level = levels.get('info')

def create_logger(name, formater=defaultfmt, levelname=None, file=None):
	global logger, logfile, level, g_levelname
	if logfile == -1:
		logfile = file
	if logger:
		return logger
	logger = logging.getLogger(name)
	if levelname:
		g_levelname = levelname
	else:
		levelname = g_levelname
	level = levels.get(levelname, levels.get('info'))
	logger.setLevel(level)
	format = logging.Formatter(formater)
	file_handler = None
	if logfile is not None:
		file_handler = logging.FileHandler(logfile)
	else:
		file_handler = logging.StreamHandler()
	
	file_handler.setFormatter(format)
	logger.addHandler(file_handler)
	return logger


def info(*args, **kw):
	global logger
	if logger is None:
		return
	logger.info(*args, **kw)

def debug(*args, **kw):
	global logger
	if logger is None:
		return
	logger.debug(*args, **kw)

def warning(*args, **kw):
	global logger
	if logger is None:
		return
	logger.warning(*aegs, **kw)

def error(*args, **kw):
	global logger
	if logger is None:
		return
	logger.error(*args, **kw)

def critical(*args, **kw):
	global logger
	if logger is None:
		return
	logger.critical(*args, **kw)

def exception(*args, **kw):
	global logger
	if logger is None:
		return
	logger.exception(**args, **kw)

class AppLogger:
	def __init__(self):
		self.logger = create_logger(self.__class__.__name__)
		self.debug = self.logger.debug
		self.info = self.logger.info
		self.warning = self.logger.warning
		self.error = self.logger.error
		self.critical = self.logger.critical
		self.exception = self.logger.exception
