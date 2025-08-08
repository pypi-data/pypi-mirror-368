import time
import random
import asyncio
import inspect
import concurrent
from functools import wraps
from functools import wraps

def awaitify(sync_func):
	"""Wrap a synchronous callable to allow ``await``'ing it"""
	@wraps(sync_func)
	async def async_func(*args, **kw):
		loop = None
		try:
			loop = asyncio.get_event_loop()
		except:
			loop = asyncio.new_event_loop()
		# Run the blocking generation in a background thread
		with concurrent.futures.ThreadPoolExecutor() as pool:
			return await loop.run_in_executor(pool, 
								lambda:sync_func(*args, **kw))
	return async_func

def to_func(func):
	@wraps(func)
	def wraped_func(*args,**kw):
		if inspect.iscoroutinefunction(func):
			task =  asyncio.ensure_future(func(*args,**kw))
			ret = asyncio.gather(task)
			return ret
		return func(*args, **kw)
	return wraped_func

class AsyncWorker:
	def __init__(self,maxtask=50):
		self.semaphore = asyncio.Semaphore(maxtask)

	async def __call__(self,callee,*args,**kw):
		async with self.semaphore:
			if inspect.iscoroutinefunction(callee):
				return await callee(*args,**kw)
			return callee(*args, **kw)

	async def run(self,cmd):
		async with self.semaphore:
			proc = await asyncio.create_subprocess_shell(cmd,
				stdout=asyncio.subprocess.PIPE,
				stderr=asyncio.subprocess.PIPE)

			stdout, stderr = await proc.comunicate()
			return stdout, stderr

if __name__ == '__main__':
	def hello(cnt,greeting):
		t = random.randint(1,10)
		print(cnt,'will sleep ',t,'seconds')
		time.sleep(t)
		print(cnt,'cost ',t,'seconds to',greeting)

	async def ahello(cnt,greeting):
		t = random.randint(1,10)
		print(cnt,'will sleep ',t,'seconds')
		await asyncio.sleep(t)
		print(cnt,'cost ',t,'seconds to',greeting)

	async def run():
		w = AsyncWorker()
		f = awaitify(hello)
		g = [ asyncio.create_task(w(f,i,'hello world')) for i in range(100) ]
		await asyncio.wait(g)
		print('aaaaaaaaaaaaaaaaaaa')

	loop = asyncio.get_event_loop()
	loop.run_until_complete(run())
	
