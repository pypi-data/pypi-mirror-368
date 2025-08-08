from threading import Thread

class Background(Thread):
	def __init__(self,func, *args,**kw):
		Thread.__init__(self)
		self.__callee = func
		self.__args = args
		self.__kw = kw

	def run(self):
		return self.__callee(*self.__args, **self.__kw)
