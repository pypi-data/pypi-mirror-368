import time
import threading
import random
from appPublic.background import Background

class ThreadWorkers:
	def __init__(self, max_workers=10):
		self.semaphore = threading.Semaphore(value=max_workers)
		self.co_worker = 0
	def _do(self, func, *args, **kwargs):
		try:
			self.semaphore.acquire()
			self.co_worker += 1
			func(*args, **kwargs)
		finally:
			self.co_worker -= 1
			self.semaphore.release()
		

	def do(self, func, *args, **kwargs):
		b = Background(self._do, func, *args, **kwargs)
		b.start()

	def get_workers(self):
		return self.co_worker

	def until_done(self):
		time.sleep(0.1)
		while self.co_worker > 0:
			time.sleep(0.01)
		
if __name__ == '__main__':
	def k(worker):
		t = random.randint(1,4)
		print('current workers=',worker.get_workers(), 'sleep=', t)
		time.sleep(t)

	w = ThreadWorkers(max_workers=30)
	for i in range(100000):
		w.do(k, w)
	
