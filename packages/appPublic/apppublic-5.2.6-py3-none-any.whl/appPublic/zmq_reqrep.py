# zmq_reqresp.py
import asyncio
import zmq
import zmq.asyncio
from .background import Background
from inspect import iscoroutinefunction

class ZmqRequester(object):
	def __init__(self, url, async_mode=False, timeout=0):
		super().__init__()
		self.async_mode = async_mode
		self.url = url
		self.timeout = timeout
		self._connect()

	def __del__(self):
		self._close()

	def _connect(self):
		if self.async_mode:
			self.ctx = zmq.asyncio.Context()
		else:
			self.ctx = zmq.Context()

		#  Socket to talk to server
		self.sock = self.ctx.socket(zmq.REQ)
		self.sock.connect(self.url)
		if self.timeout > 0:
			self.sock.setsockopt(zmq.LINGER, 0)
			self.poller = zmq.Poller()
			self.poller.register(self.sock, zmq.POLLIN)

	def _close(self):
		self.sock.close()
		self.ctx.term()

	def send(self, msg):
		"""
		send s string to responser, and return a string
		"""
		if self.async_mode:
			raise Exception('ZMQ_Requester: in async mode, use asend instead')
		b = msg.encode('utf-8')
		r = self.send_b(b)
		if r is not None:
			return r.decode('utf-8')
		return None

	def send_b(self, b):
		"""
		send a bytes and return a bytes
		"""
		if self.async_mode:
			raise Exception('ZMQ_Requester: in async mode, use asend_b instead')
		self.sock.send(b)
		if self.timeout > 0:
			if self.poller.poll(self.timeout * 1000):
				return self.sock.recv()
			else:
				self._close()
				self._connect()
				return None
		else:
			return self.sock.recv()

	async def asend_b(self, b):
		if not self.async_mode:
			raise Exception('ZMQ_Requester: not in async mode, use send_b instead')
		await self.sock.send_multipart([b])
		if self.timeout > 0:
			if self.poller.poll(self.timeout * 1000):
				r = await self.sock.recv_multipart()
				return r
			else:
				self._close()
				self._connect()
				return None
		r = await self.sock.recv_multipart()
		return r[0]

	async def asend(self, msg):
		if not self.async_mode:
			raise Exception('ZMQ_Requester: not in async mode, use send instead')
		b = msg.encode('utf-8')
		r = await self.asend_b(b)
		if r is None:
			return None
		return r.decode('utf-8')

class ZmqReplier(object):
	def __init__(self, url, handler, async_mode=False):
		self.async_mode = async_mode
		self.url = url
		if not self.async_mode and iscoroutinefunction(handler):
			raise('not in async mode, handler can not be a coroutine')

		self.handler = handler
		if self.async_mode:
			self.ctx = zmq.asyncio.Context()
		else:
			self.ctx = zmq.Context()
		self.sock = self.ctx.socket(zmq.REP)
		self.sock.bind(self.url)
		self.keep_running = True
		
	async def async_run(self):
		while self.keep_running:
			bs = await self.sock.recv_multipart()
			b = b[0]
			if iscoroutinefunction(self.handler):
				rb = await self.handler(b)
			else:
				rb =self.self.handler(b)

			if isinstance(rb, str):
				rb = rb.encode('utf-8')
			await self.sock.send_multipart([rb])

	def run(self):
		self.background = Background(self._run)
		self.background.daemon = True
		self.background.start()

	def _run(self):
		while self.keep_running:
			b = self.sock.recv()
			
			rb = self.handler(b)
			if isinstance(rb, str):
				rb = rb.encode('utf-8')
			self.sock.send(rb)

	def stop(self):
		self.keep_running = False
		self.join()
