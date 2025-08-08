import sys
import codecs
from traceback import format_exc
from appPublic.timeUtils import timestampstr
from appPublic.Singleton import SingletonDecorator
import inspect

def my_function():
    frame_info = inspect.currentframe()
    caller_frame = frame_info.f_back
    file_name = inspect.getframeinfo(caller_frame).filename
    line_number = inspect.getframeinfo(caller_frame).lineno
    print(f"Called from file: {file_name}, line: {line_number}")


@SingletonDecorator
class MyLogger:
	levels={
		"clientinfo":7,
		"info":6,
		"debug":5,
		"warning":4,
		"error":3,
		"exception":2,
		"critical":1
	}
	formater='%(timestamp)s[%(name)s][%(levelname)s][%(filename)s:%(lineno)s]%(message)s\n'
	def __init__(self, name, levelname='debug', logfile=None):
		self.name = name
		self.levelname = levelname
		self.level = self.levels.get(levelname)
		self.logfile = logfile
	
	def open_logger(self):
		if self.logfile:
			self.logger = codecs.open(self.logfile, 'a', 'utf-8')
		else:
			self.logger = sys.stdout
	
	def close_logger(self):
		if self.logfile:
			self.logger.close();
			self.logger = None
		self.logger = None
	
	def log(self, levelname, message, frame_info):
		caller_frame = frame_info.f_back
		filename = inspect.getframeinfo(caller_frame).filename
		lineno = inspect.getframeinfo(caller_frame).lineno
		level = self.levels.get(levelname)
		if level > self.level:
			print(f'{level=},{self.level=}')
			return
		data = {
			'timestamp':timestampstr(),
			'name':self.name,
			'levelname':levelname,
			'message':message,
			'filename':filename,
			'lineno':lineno
		}
		self.open_logger()
		s = self.formater % data
		self.logger.write(s)
		self.logger.flush()
		self.close_logger()
	
def clientinfo(message):
	frame_info = inspect.currentframe()
	logger = MyLogger('Test')
	logger.log('clientinfo', message, frame_info)

def info(message):
	frame_info = inspect.currentframe()
	logger = MyLogger('Test')
	logger.log('info', message, frame_info)

def debug(message):
	frame_info = inspect.currentframe()
	logger = MyLogger('Test')
	logger.log('debug', message, frame_info)

def warning(message):
	frame_info = inspect.currentframe()
	logger = MyLogger('Test')
	logger.log('warning', message, frame_info)

def error(message):
	frame_info = inspect.currentframe()
	logger = MyLogger('Test')
	logger.log('error', message, frame_info)

def critical(message):
	frame_info = inspect.currentframe()
	logger = MyLogger('Test')
	logger.log('critical', message, frame_info)

def exception(message):
	frame_info = inspect.currentframe()
	tb_msg =  format_exc()
	msg = f'{message}\n{tb_msg}'
	logger = MyLogger('exception')
	logger.log('exception', msg, frame_info)

