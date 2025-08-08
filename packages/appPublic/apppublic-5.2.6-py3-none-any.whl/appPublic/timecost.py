import time
import datetime
from .Singleton import SingletonDecorator

timerecord = {}

class TimeCost:
	def __init__(self,name):
		self.name = name
	
	def __enter__(self):
		self.begin_time = time.time()
	
	def __exit__(self,*args):
		self.end_time = time.time()
		d = timerecord.get(self.name,[])
		d.append(self.end_time - self.begin_time)
		timerecord[self.name] = d

	def clear(self):
		timerecord = {}

	@classmethod
	def clear_all(self):
		timerecord = {}

	@classmethod
	def clear(self, name):
		timerecord[name] = []

	@classmethod
	def show(self):
		def getTimeCost(name):
			x = timerecord.get(name,[])
			if len(x) == 0:
				return 0,0,0
			return len(x), sum(x), sum(x)/len(x)
		
		print('TimeCost ....')
		for name in timerecord.keys():
			print(name, * getTimeCost(name))

