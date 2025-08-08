
from natpmp import NATPMP as pmp
from aioupnp.upnp import UPnP
from requests import get
from .background import Background

class AcrossNat(object):
	def __init__(self):
		self.external_ip = None
		self.upnp = None
		self.pmp_supported = True
		self.upnp_supported = True
		self.init_pmp()

	async def init_upnp(self):
		if self.upnp is None:
			self.upnp = await UPnP.discover()

	def init_pmp(self):
		try:
			self.external_ip = pmp.get_public_address()
		except pmp.NATPMPUnsupportedError:
			self.pmp_supported = False

	async def get_external_ip(self):
		if self.pmp_supported:
			self.external_ip = pmp.get_public_address()
			return self.external_ip

		if self.upnp_supported:
			if self.upnp is None:
				await self.init_upnp()
			return await self.upnp.get_external_ip()

		try:
			return get('https://api.ipify.org').text
		except:
			return get('https://ipapi.co/ip/').text

	async def upnp_map_port(self, inner_port, 
							protocol='TCP', from_port=40003, ip=None, desc=None):

		if self.upnp is None:
			await self.init_upnp()
		protocol = protocol.upper()
		if ip is None:
			ip = self.upnp.lan_address

		all_mappings = [i for i in await self.upnp.get_redirects()]
		x = [ i for i in all_mappings if i.internal_port == inner_port \
										and i.lan_address == ip \
										and i.protocol == protocol ]
		if len(x) > 0:
			return x[0].external_port

		occupied_ports = [ i.external_port for i in all_mappings if i.protocol == protocol ]
		external_port = from_port
		while external_port < 52333:
			if external_port not in occupied_ports:
				break
			external_port += 1

		if external_port < 52333:
			await self.upnp.add_port_mapping(external_port,
									protocol,
									inner_port,
									ip,
									desc or 'user added')
			return external_port
		return None

	async def is_port_mapped(self, external_port, protocol='TCP'):
		if self.upnp is None:
			await self.init_upnp()
		protocol = protocol.upper()
		if self.upnp_supported:
			x = await self.upnp.get_specific_port_mapping(external_port, 
									protocol)
			if len(x) == 0:
				return True
			return False
		raise Exception('not implemented')

	async def port_unmap(self, external_port, protocol='TCP'):
		if self.upnp is None:
			await self.init_upnp()
		protocol = protocol.upper()
		if self.upnp_supported:
			await self.upnp.delete_port_mapping(external_port, protocol)
		raise Exception('not implemented')

	def pmp_map_port(self, inner_port, protocol='TCP', from_port=40003):
		if protocol.upper() == 'TCP':
			x = pmp.map_tcp_port(from_port, inner_port, 
								lifetime=999999999)
			return x.public_port
		x = pmp.map_udp_port(from_port, inner_port,
								lifetime=999999999)
		return x.public_port

	async def map_port(self, inner_port, protocol='tcp', from_port=40003, lan_ip=None, desc=None):
		if self.pmp_supported:
			return self.pmp_map_port(inner_port, protocol=protocol)

		return await self.upnp_map_port( inner_port, protocol=protocol, ip=lan_ip, desc=desc)

