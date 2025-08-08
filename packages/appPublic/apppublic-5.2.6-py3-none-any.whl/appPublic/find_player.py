# !/usr/bin/env python
# -*- coding:UTF-8 -*-
from socket import *
import json
from appPublic.sockPackage import get_free_local_addr
from appPublic.background import Background
BUFSIZE = 1024
class BroadcastServer:
	def __init__(self, port, info):
		self.info = info
		self.port = port
		self.udpSerSock = socket(AF_INET, SOCK_DGRAM)
		# 设置阻塞
		self.udpSerSock.setblocking(1)
		# 设置超时时间 1s
		# self.udpSerSock.settimeout(1)
		self.udpSerSock.bind(('' ,port))
		self.run_flg = True
		self.thread = Background(self.run)
		self.thread.start()
	
	def run(self):
		while self.run_flg:
			try:
				data, addr = self.udpSerSock.recvfrom(BUFSIZE)
				ret = json.dumps(self.info).encode('utf-8')
				self.udpSerSock.sendto(ret, addr)
			except Exception as e:
				print('exception happened:',e)
				pass

	def stop(self):
		self.run_flg = False
		self.udpSerSock.close()
		
def find_players(port):
	# broadcast_addr = '.'.join(host.split('.')[:-1]) + '.255'
	host = get_free_local_addr()[0]
	udpCliSock = socket(AF_INET, SOCK_DGRAM)
	#设置阻塞
	#udpCliSock.setblocking(2)
	#设置超时时间
	udpCliSock.settimeout(5)
	udpCliSock.bind(('', 0))  
	udpCliSock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)  
	udpCliSock.sendto(b'findplayers', ('255.255.255.255',port))
	players = []
	while True:
		try:
			data,addr = udpCliSock.recvfrom(BUFSIZE)
			if  addr[0] != host and data:
				data = data.decode('utf-8')
				d = json.loads(data)
				d['ip'] = addr[0]
				players.append(d)
		except Exception as e:
			break
	udpCliSock.close()
	return players

