import asyncio
from inspect import isfunction, iscoroutinefunction
from functools import partial
from appPublic.dictObject import DictObject
from appPublic.worker import awaitify
from appPublic.Singleton import SingletonDecorator
from appPublic.log import info, error

@SingletonDecorator
class RegisterFunction:
	def __init__(self):
		self.registKW = {}

	def register(self,name,func):
		if not isfunction(func) and not iscoroutinefunction(func):
			error(f'RegisterFunction.register({name}, {func}): func is not a function or routine')
			return
		self.registKW[name] = func
	
	def get(self,name):
		return self.registKW.get(name,None)
	
	def run(self, name, *args, **kw):
		f = self.get(name)
		if iscoroutinefunction(f):
			print(f'{name} is a coro')
			return None
		if f:
			return f(*args, **kw)
		error(f'{name} not register')

	async def exe(self, name, *args, **kw):
		f = self.get(name)
		if f is None:
			# error(f'{name=} function not registed')
			return None
		if iscoroutinefunction(f):
			# info(f'{name=} is coroutine function');
			return await f(*args, **kw)
		f1 = awaitify(f)
		return f1(*args, **kw)

@SingletonDecorator
class RegisterCoroutine:
	def __init__(self):
		self.kw = DictObject()
	
	def register(self, name, func):
		if not isfunction(func) and not iscoroutinefunction(func):
			error(f'RegisterFunction.register({name}, {func}): func is not a function or routine')
			return
		if not self.kw.get(name):
			self.kw[name] = [func]
		else:
			self.kw[name].append(func)
	async def exe(self, name, *args, **kw):
		fs = self.kw.get(name)
		if fs is None:
			return
		fs = fs.copy()
		fs.reverse()
		if fs:
			for f in fs:
				if iscoroutinefunction(f):
					await f(*args, **kw)
				else:
					f(*args, **kw)
		return None

def getRegisterFunctionByName(name):
	rf = RegisterFunction()
	return rf.get(name)

def registerFunction(name, func):
	rf = RegisterFunction()
	rf.register(name, func)

async def rfexe(rfname, *args, **kw):
	rf = RegisterFunction()
	return await rf.exe(rfname, *args, **kw)

def rfrun(rfname, *args, **kw):
	rf = RegisterFunction()
	return rf.run(rfname, *args, **kw)

async def main():
	d = {}
	rf = RegisterCoroutine()
	rf.register('test', z)
	rf.register('test', y)
	rf.register('test', x)
	nd = await rf.exe('test', d)
	print(nd)

if __name__ == '__main__':
	def x(dic):
		dic['a'] = 'a'
		return dic

	async def y(dic):
		dic['b'] = 'b'
		return dic
	
	def z(dic):
		dic['c'] = 1
		return dic

	asyncio.get_event_loop().run_until_complete(main())
