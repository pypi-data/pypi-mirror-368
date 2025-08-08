import socket
import socks
import requests

original_socket = socket.socket

def set_socks_proxy(host, port):
	socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, host, port)
	socket.socket = socks.socksocket

def unset_proxy():
	socket.socket = original_socket
