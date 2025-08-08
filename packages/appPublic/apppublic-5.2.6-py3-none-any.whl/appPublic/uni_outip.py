import os
import time
from natpmp import NATPMP as pmp
import upnpclient
from appPublic.ipgetter import IPgetter
from multiprocessing import Process, Pipe

def pmp_get_external_ip():
	try:
		return pmp.get_public_address()
	except:
		return None

def upnp_get_external_ip():
	try:
		igd = upnpclient.discover()[0]
		print(igd.service_map)

		s_names = [ n for n in igd.service_map.keys() if 'WAN' in n and 'Conn' in n]
		upnp = igd.service_map[s_names[0]]
		x = upnp.GetExternalIPAddress()
		return x.get('NewExternalIPAddress', None)
	except Exception as e:
		print(f'e={e}')
		return None
	
def ipgetter_get_external_ip():
	getter = IPgetter()
	ip = None
	while ip is None:
		try:
			ip = getter.get_external_ip()
		except:
			ip = None
		if ip:
			return ip
		time.sleep(0.1)

def get_external_ip():
	ip = pmp_get_external_ip()
	if ip:
		return ip
	ip = upnp_get_external_ip()
	if ip:
		return ip
	return ipgetter_get_external_ip()

def outip(w):
	os.dup2(w.fileno(), 1)
	ip = get_external_ip()
	print(ip)

def get_ip():
	r, w = Pipe()
	reader = os.fdopen(r.fileno(), 'r')
	p = Process(None, outip, 'TESTER', (w, ))
	p.start()
	ip = reader.readline()
	p.join()
	return ip.strip()

def run():
	while True:
		ip = get_ip()
		if ip:
			print(f'{ip=}')
		time.sleep(10)

if __name__ == '__main__':
	run()
