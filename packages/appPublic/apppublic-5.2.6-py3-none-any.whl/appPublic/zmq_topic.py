import sys
import zmq
import time
from zmq import Context
from appPublic.jsonConfig import getConfig

class TopicServer:
	def __init__(self, address='127.0.0.1', pub_port='5566', sub_port='5567'):
		# get ZeroMQ version
		print("Current libzmq version is %s" % zmq.zmq_version())
		print("Current  pyzmq version is %s" % zmq.pyzmq_version())

		self.context = Context.instance()
		# 2 sockets, because we can only bind once to a socket (as opposed to connect)
		self.pub_port = "tcp://{}:{}".format(address, pub_port)
		self.sub_port = "tcp://{}:{}".format(address, sub_port)

		self.xpub_xsub_proxy()

	# N publishers to 1 sub; proxy 1 sub to 1 pub; publish to M subscribers
	def xpub_xsub_proxy(self):
		print("Init proxy")

		# Socket subscribing to publishers
		frontend_pubs = self.context.socket(zmq.XSUB)
		frontend_pubs.bind(self.pub_port)

		# Socket publishing to subscribers
		backend_subs = self.context.socket(zmq.XPUB)
		backend_subs.bind(self.sub_port)

		print("Try: Proxy... CONNECT!")
		zmq.proxy(frontend_pubs, backend_subs)
		print("CONNECT successful!")
		"""
		while True:
			time.sleep(1)
		"""

class ConfiguredTopicServer(TopicServer):
	"""
	in config file has a topicserver key
	{
		"topicserver":{
			"address":"11.11.1.11",
			"pub_port":1234,
			"sub_server":1235
		}
	}
	"""
	def __init__(self):
		config = getConfig()
		params = config.topicserver
		if not params:
			raise MissTopicServerConfig
		super(ConfiguredTopicServer, self).__init__(**params)

class TopicPublisher:
	def __init__(self, topic='en', address='127.0.0.1', port='5566'):
		# get ZeroMQ version
		print("Current libzmq version is %s" % zmq.zmq_version())
		print("Current  pyzmq version is %s" % zmq.pyzmq_version())

		self.topic = topic
		self._topic = topic.encode('utf-8')
		self.context = Context.instance()
		self.url = "tcp://{}:{}".format(address, port)
		self.pub = self.context.socket(zmq.PUB)
		self.pub.connect(self.url)
		time.sleep(0.5)

	def send(self, message):
		self.pub.send_multipart([self._topic, message.encode('utf-8')])

class ConfiguredTopicPublisher(TopicPublisher):
	def __init__(self, topic=''):
		config = getConfig()
		params = config.topicserver
		if not params:
			raise MissTopicServerConfig
		super(ConfiguredTopicPublisher, self).__init__(topic=topic, 
					address = params.address,
					port=params.pub_port)
		
class TopicSubscriber:
	def __init__(self, topic='', address='127.0.0.1', port='5567', callback=None):
		# get ZeroMQ version
		print("Current libzmq version is %s" % zmq.zmq_version())
		print("Current  pyzmq version is %s" % zmq.pyzmq_version())

		self.callback = callback
		self.topic = topic
		self.context = Context.instance()
		self.url = "tcp://{}:{}".format(address, port)
		self.sub = self.context.socket(zmq.SUB)
		self.sub.connect(self.url)
		# subscribe to topic 'en' or 'jp'
		if isinstance(self.topic, list):
			for t in self.topic:
				self.sub.setsockopt(zmq.SUBSCRIBE, t.encode('utf-8'))
		else:
			self.sub.setsockopt(zmq.SUBSCRIBE, self.topic.encode('utf-8'))


	def run(self):
		# keep listening to all published message, filtered on topic
		print("Sub {}: Going to wait for messages!".format(self.topic))
		while True:
			msg_received = self.sub.recv_multipart()
			print("sub {}: {}".format(self.topic, msg_received))
			if self.callback:
				self.callback(msg_received)

class ConfiguredTopicSubscriber(TopicSubscriber):
	def __init__(self, topic=''):
		config = getConfig()
		params = config.topicserver
		if not params:
			raise MissTopicServerConfig
		super(ConfiguredTopicSubscriber, self).__init__(topic=topic, 
						address=params.address,
						port=params.sub_port)
		
