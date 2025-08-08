
from traceback import print_exc
from natpmp import NATPMP as pmp
import upnpclient
from requests import get
from .background import Background

class AcrossNat(object):
	def __init__(self):
		self.external_ip = None
		self.upnp = None
		self.pmp_supported = True
		self.upnp_supported = True
		self.init_pmp()
		self.init_upnp()

	def init_upnp(self):
		try:
			igd = upnpclient.discover()[0]
			s_names = [ n for n in igd.service_map.keys() if 'WAN' in n and 'Conn' in n]
			self.upnp = igd.service_map[s_names[0]]
		except Exception as e:
			print(e)
			print_exc()
			self.upnp_supported = False

	def init_pmp(self):
		try:
			self.external_ip = pmp.get_public_address()
		except pmp.NATPMPUnsupportedError:
			self.pmp_supported = False

	def get_external_ip(self):
		if self.pmp_supported:
			try:
				self.external_ip = pmp.get_public_address()
				return self.external_ip
			except:
				self.pmp_supported = False

		if self.upnp_supported:
			try:
				x = self.upnp.GetExternalIPAddress()
				return x['NewExternalIPAddress']
			except:
				self.upnp_supported = False
		try:
			return get('https://api.ipify.org').text
		except:
			pass
		try:
			return get('https://ipapi.co/ip/').text
		except:
			return None

	def upnp_check_external_port(self, eport, protocol='TCP'):
		try:
			self.upnp.GetSpecificPortMappingEntry(NewExternalPort=eport, 
			NewProtocol=protocol, 
			NewRemoteHost='')
			return True
		except:
			return False

	def upnp_map_port(self, inner_port, 
							protocol='TCP', from_port=40003, 
							ip=None, desc='test'):

		protocol = protocol.upper()
		external_port = from_port
		while external_port < 52333:
			if self.upnp_check_external_port(external_port, 
									protocol=protocol):
				external_port += 1
				continue
			try:
				self.upnp.AddPortMapping(NewRemoteHost='',
						NewExternalPort=external_port,
						NewProtocol=protocol,
						NewInternalPort=inner_port,
						NewInternalClient=ip,
						NewEnabled='1',
						NewPortMappingDescription=desc,
						NewLeaseDuration=0
				)
				return external_port
			except:
				return None
		return None

	def is_port_mapped(self, external_port, protocol='TCP'):
		protocol = protocol.upper()
		if self.upnp_supported:
			return self.upnp_check_external_port(external_port, 
									protocol=protocol)
		raise Exception('not implemented')

	def port_unmap(self, external_port, protocol='TCP'):
		protocol = protocol.upper()
		if self.upnp_supported:
			self.upnp.delete_port_mapping(external_port, protocol)
		raise Exception('not implemented')

	def pmp_map_port(self, inner_port, protocol='TCP', from_port=40003):
		if protocol.upper() == 'TCP':
			x = pmp.map_tcp_port(from_port, inner_port, 
								lifetime=999999999)
			return x.public_port
		x = pmp.map_udp_port(from_port, inner_port,
								lifetime=999999999)
		return x.public_port

	def map_port(self, inner_port, protocol='tcp', from_port=40003, lan_ip=None, desc=None):
		if self.pmp_supported:
			return self.pmp_map_port(inner_port, protocol=protocol)

		return self.upnp_map_port( inner_port, protocol=protocol, ip=lan_ip, desc=desc)

