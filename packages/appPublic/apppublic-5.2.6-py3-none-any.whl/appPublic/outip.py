import re
import time
import requests

class IpGetter:
	def __init__(self, url, parser):
		self.url = url
		self.parser = parser
		self.cnt = 0
		self.total_time = 0
		self.avg_time = 0
	
	def get(self):
		try:
			tim1 = time.time()
			r = requests.get(self.url)
			txt = r.text
			ip = self.parser(txt)
			tim2 = time.time()
			cost_tim = tim2 - tim1
			self.cnt += 1
			self.total_time += cost_tim
			self.avg_time = self.total_time / self.cnt
			ret = self.check_ip(ip)
			if ret:
				return ret
			self.avg_time = 10000
			print('Error, get=', ip)
			return None
		except Exception as e:
			print(f'{self.url=}. {e=}')
			self.avg_time = cost_tim = 10000
			return None

	def check_ip(self, ip):
		ret = re.compile(r'(\d+.\d+.\d+.\d+)').search(ip)
		if ret:
			return ret.group(1)
		print('ip format check failed', ip, self.url)
		return None

	def get_average_time(self):
		return self.avg_time
	
	def __str__(self):
		return f'{self.url=},{self.avg_time=}'

class OutIP:
	def __init__(self):
		self.getters = []
		self.set_known_getters()
	
		
	def set_known_getters(self):
		g = IpGetter('http://ipinfo.io/ip', lambda x: x)
		self.add_getter(g)
		g = IpGetter('https://api.ipify.org', lambda x: x)
		self.add_getter(g)
		g = IpGetter('https://ident.me', lambda x: x)
		self.add_getter(g)
		# g = IpGetter('https://ipapi.co/ip/', lambda x: x)
		# self.add_getter(g)
		g = IpGetter('http://myip.dnsomatic.com', lambda x: x)
		self.add_getter(g)
		g = IpGetter('https://checkip.amazonaws.com', lambda x: x.strip())
		self.add_getter(g)
		def f(t):
			return re.compile(r'Address: (\d+.\d+.\d+.\d+)').search(t).group(1)
		g = IpGetter('http://checkip.dyndns.com', f)
		self.add_getter(g)
	
	def add_getter(self, getter):
		self.getters.append(getter)
	
	def get(self):
		gs = self.getters.copy()
		gs.sort(key=lambda a: a.get_average_time())
		for g in gs:
			# print(*[str(g) for g in self.getters ])
			ip =  g.get()
			if ip:
				return ip
		return None

if __name__ == '__main__':
	oi = OutIP()
	i = 0
	while i < 100:
		ip = oi.get()
		print('ip = ', ip)
		time.sleep(1)
		i += 1
	
