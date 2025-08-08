# -*- coding:UTF-8 -*-
import time
from traceback import print_exc
from socket import *
from select import select

import json
from appPublic.sockPackage import get_free_local_addr
from appPublic.background import Background
BUFSIZE = 1024 * 64
class UdpComm:
	def __init__(self, port, callback, timeout=0):
		self.buffer = []
		self.callback = callback
		self.timeout = timeout
		self.host = get_free_local_addr()[0]
		self.port = port
		self.udpSerSock = socket(AF_INET, SOCK_DGRAM)
		# 设置阻塞
		# self.udpSerSock.setblocking(1 if timeout > 0 else 0)
		# 设置超时时间 1s
		# self.udpSerSock.settimeout(timeout)
		self.udpSerSock.bind(('' ,port))
		self.run_flg = True
		self.thread = Background(self.run)
		self.thread.start()
	
	def run(self):
		sock = self.udpSerSock
		while self.run_flg:
			outs = []
			if len(self.buffer) > 0:
				outs = [sock]
			in_s, out_s, exc_s = select([sock], outs, [], 0.1)
			if sock in in_s:
				b, addr = sock.recvfrom(BUFSIZE)
				t = b[0]
				b = b[1:]
				if t == 'b':
					self.callback(b, addr)
				else:
					try:
						txt = b.decode('utf-8')
						d = json.loads(txt)
						self.callback(d, addr)
					except Exception as e:
						print('except:',e)
						print_exc()
						print(t, b)
						break
			if sock in out_s:
				while len(self.buffer) > 0:
					d,addr = self.buffer.pop(0)	
					sock.sendto(d, addr)
			time.sleep(0.1)
		self.run_flg = False
		self.udpSerSock.close()

	def stop(self):
		self.run_flg = False
		self.udpSerSock.close()
		self.thread.join()
		
	def broadcast(self, data):
		broadcast_host = '.'.join(self.host.split('.')[:-1]) + '.255'
		udpCliSock = socket(AF_INET, SOCK_DGRAM)
		# udpCliSock.settimeout(1)
		udpCliSock.bind(('', 0))  
		udpCliSock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)  
		b = data
		if not isinstance(data, bytes):
			b = json.dumps(data).encode('utf-8')
		udpCliSock.sendto(b, (broadcast_host,self.port))
	
	def send(self,data,addr):
		b = data
		if not isinstance(data, bytes):
			b = b'j' + json.dumps(data).encode('utf-8')
		else:
			b = b'b' + data
		if isinstance(addr,list):
			addr = tuple(addr)
		self.buffer.append((b, addr))

	def sends(self,data, addrs):
		for a in addrs:
			self.send(data, a)

if __name__ == '__main__':
	import sys
	def msg_handle(data, addr):
		print('addr:', addr, 'data=', data, len(data))

	port = 50000
	if len(sys.argv)>1:
		port = int(sys.argv[1])
	d = UdpComm(port, msg_handle)
	x = input()
	while x:
		port, data = x.split(':')
		d.send(data, ('', int(port)))
		x = input()

