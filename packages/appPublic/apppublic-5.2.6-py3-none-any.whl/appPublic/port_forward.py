import sys
import select
import paramiko
import socket
from appPublic.background import Background
try:
	import SocketServer
except ImportError:
	import socketserver as SocketServer

class ForwardServer(SocketServer.ThreadingTCPServer):
	daemon_threads = True
	allow_reuse_address = True
	server_ready = False
	ready_callback = None
	def service_actions(self):
		super().service_actions()
		if not self.server_ready:
			self.server_ready = True
			if self.ready_callback:
				self.ready_callback()

	def shutdown(self):
		self.server_ready = False
		super().shutdown()

g_verbose = True
def verbose(s):
	if g_verbose:
		print(s)

class Handler(SocketServer.BaseRequestHandler):
	def handle(self):
		try:
			chan = self.ssh_transport.open_channel(
				"direct-tcpip",
				(self.chain_host, self.chain_port),
				self.request.getpeername(),
			)
		except Exception as e:
			verbose(
				"Incoming request to %s:%d failed: %s"
				% (self.chain_host, self.chain_port, repr(e))
			)
			return
		if chan is None:
			verbose(
				"Incoming request to %s:%d was rejected by the SSH server."
				% (self.chain_host, self.chain_port)
			)
			return

		verbose(
			"Connected!  Tunnel open %r -> %r -> %r"
			% (
				self.request.getpeername(),
				chan.getpeername(),
				(self.chain_host, self.chain_port),
			)
		)
		while True:
			r, w, x = select.select([self.request, chan], [], [])
			if self.request in r:
				data = self.request.recv(1024)
				if len(data) == 0:
					break
				chan.send(data)
			if chan in r:
				data = chan.recv(1024)
				if len(data) == 0:
					break
				self.request.send(data)

		peername = self.request.getpeername()
		chan.close()
		self.request.close()
		verbose("Tunnel closed from %r" % (peername,))

def connect_ssh_server(host, port, user, password):
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(host, port=port, username=user, 
		password=password)
	return ssh

class SSHPortForward:
	def __init__(self, local_port, remote_host, remote_port, 
					ssh_host, ssh_port, ssh_user, ssh_password):
		self.local_port = int(local_port)
		self.remote_host = remote_host
		self.remote_port = int(remote_port)
		self.ssh_host = ssh_host
		self.ssh_port = int(ssh_port)
		self.ssh_user = ssh_user
		self.ssh_password = ssh_password
		self.running = False
		self._ready = False

	def service_ready(self):
		print('servie ready .....')
		self._ready = True

	def run(self):
		if self.running:
			return
		self.running = True
		b = Background(self._run)
		b.start()

	def _run(self):
		self.ssh = connect_ssh_server(self.ssh_host,
						self.ssh_port,
						self.ssh_user,
						self.ssh_password)

		self.transport = self.ssh.get_transport()
		class MyForwardServer(ForwardServer):
			ready_callback = self.service_ready

		class SubHandler(Handler):
			chain_host = socket.gethostbyname(self.remote_host)
			chain_port = self.remote_port
			local_port = self.local_port
			ssh_transport = self.transport

		self.forward_server = MyForwardServer((socket.gethostbyname('localhost'), self.local_port), SubHandler)
		self.forward_server.serve_forever()
		print('forward ....')

	def stop(self):
		if not self.running:
			return
		self.running = False
		self.forward_server.shutdown()
		self.forward_server.server_close()
		self.transport.close()
		self.ssh.close()

if __name__ == '__main__':
	if len(sys.argv) < 8:
		print("""Usage:
{sys.argv[0] local_port remote_host remote_port ssh_host ssh_port ssh_user ssh_password
""")
		sys.exit(1)
	s = SSHPortForward(*sys.argv[1:])
	while True:
		print("""start) start server,
stop) stop server
quit) quit
""")
		x = input()
		if x == 'start':
			s.run()
			continue
		if x == 'stop':
			s.stop()
			continue
		if x == 'quit':
			s.stop()
			break
		print('error input')
						
