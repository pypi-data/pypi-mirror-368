import os
from traceback import format_exc
import asyncio
import aiohttp
from aiohttp import FormData
import ssl
import certifi
import json
from appPublic.myTE import MyTemplateEngine
import re
from appPublic.log import info, debug, warning, error, exception, critical
from urllib.parse import urlparse
from aiohttp_socks import ProxyType, ProxyConnector, ChainProxyConnector

def get_domain(url):
	# Prepend 'http://' if the URL lacks a scheme
	if not url.startswith(('http://', 'https://')):
		url = 'http://' + url
	parsed_url = urlparse(url)
	netloc = parsed_url.netloc
	domain = netloc.split(':')[0]
	return domain

RESPONSE_BIN = 0
RESPONSE_TEXT = 1
RESPONSE_JSON = 2
RESPONSE_FILE = 3
RESPONSE_STREAM = 4

class HttpError(Exception):
	def __init__(self, code, msg, *args, **kw):
		super().__init__(*msg, **kw)
		self.code = code
		self.msg = msg
	def __str__(self):
		return f"Error Code:{self.code}, {self.msg}"
	
	def __expr__(self):
		return str(self)
	
class HttpClient:
	def __init__(self,coding='utf-8', socks5_proxy_url=None):
		self.coding = coding
		self.session = None
		self.cookies = {}
		self.proxy_connector = None
		self.socks5_proxy_url = socks5_proxy_url
		self.blocked_domains = set()
		self.load_cache()

	def save_cache(self):
		home_dir = os.path.expanduser('~')
		cache_file = os.path.join(home_dir, '.proxytarget')
		with open(cache_file, 'w') as f:
			for d in self.blocked_domains:
				f.write(f'{d}\n')

	def load_cache(self):
		# 初始化缓存文件
		home_dir = os.path.expanduser('~')
		cache_file = os.path.join(home_dir, '.proxytarget')
		
		try:
			with open(cache_file, 'r') as f:
				for line in f:
					domain = line.strip()
					if domain:
						self.blocked_domains.add(domain)
		except FileNotFoundError:
			# 创建空文件
			with open(cache_file, 'w') as f:
				pass

	async def close(self):
		if self.session:
			await self.session.close()
			self.session = None

	def setCookie(self,url,cookies):
		name = get_domain(url)
		self.cookies[name] = cookies

	def getCookies(self,url):
		name = get_domain(url)
		return self.cookies.get(name,None)

	def getsession(self,url):
		if self.session is None:
			jar = aiohttp.CookieJar(unsafe=True)
			self.session = aiohttp.ClientSession(cookie_jar=jar)
		return self.session
				
	async def response_generator(self, url, resp):
		if resp.cookies is not None:
			self.setCookie(url,resp.cookies)

		async for chunk in resp.content.iter_chunked(1024):
			yield chunk

	async def response_handle(self,url, resp, resp_type=None, stream_func=None):
		if resp.cookies is not None:
			self.setCookie(url,resp.cookies)

		if stream_func:
			async for chunk in resp.content.iter_chunked(1024):
				if stream_func:
					await stream_func(chunk)
			return None

		if resp_type == RESPONSE_BIN:
			return await resp.read()
		if resp_type == RESPONSE_JSON:
			return await resp.json()
		if resp_type == RESPONSE_TEXT:
			return await resp.text(self.coding)

	def grapCookie(self,url):
		session = self.getsession(url)
		domain = get_domain(url)
		filtered = session.cookie_jar.filter_cookies(domain)
		return filtered

	async def make_request(self, url, method='GET', 
							params=None, 
							data=None,
							jd=None,
							headers=None, 
							use_proxy=False
							):
		if use_proxy:
			connector = ProxyConnector.from_url(self.socks5_proxy_url)
			reco = aiohttp.ClientSession(connector=connector)
		else:
			reco = aiohttp.ClientSession()
		async with reco as session:
			hp = {
			}
			if params:
				hp['params'] = params	
			if data:
				hp['data'] = data
			if jd:
				hp['jd'] = jd

			if headers:
				hp['headers'] = headers
			if url.startswith('https://'):
				debug(f'{url=} add_ssl_ctx')
				hp['ssl_ctx'] = ssl.create_default_context(cafile=certifi.where())
			# debug(f'{url=}, {hp=}')
			return await session.request(method, url, 
						**hp
			)

	async def get_request_response(self, url, method='GET',
							params=None,
							data=None,
							jd=None,
							headers=None,
							**kw
			):
		domain = get_domain(url)
		try:
			if self.socks5_proxy_url is None or domain not in self.blocked_domains:
				return await self.make_request(url, method=method, 
										params=params,
										data=data,
										jd=jd,
										use_proxy=False,
										headers=headers
			)
		except:
			e = Exception(f'make_request error')
			exception(f'{e=}, {format_exc()}')
			if self.socks5_proxy_url is None:
				raise e
			debug(f'{self.socks5_proxy_url=}, {self.blocked_domains=},  {domain=}')
			if domain not in self.blocked_domains:
				self.blocked_domains.add(domain)
				self.save_cache()
		return await self.make_request(url, method=method, 
										params=params,
										data=data,
										jd=jd,
										use_proxy=True,
										headers=headers
										)

	async def request(self, url, method='GET',
							response_type=RESPONSE_TEXT,
							params=None,
							data=None,
							jd=None,
							stream_func=None,
							headers=None,
							**kw
			):
		resp = await self.get_request_response(url, method=method,
							params=params,
							data=data,
							jd=jd,
							headers=headers,
							**kw
		)
		if resp.status==200:
			return await self.response_handle(url, resp, 
					resp_type=response_type,
					stream_func=stream_func)

		msg = f'http error({resp.status}, {url=},{params=}, {data=}, {jd=})'
		exception(msg)
		raise HttpError(resp.status, msg)

	async def __call__(self, url, method='GET',
							response_type=RESPONSE_TEXT,
							params=None,
							data=None,
							jd=None,
							headers=None,
							stream=False,
							use_proxy=False,
							**kw
							):
		resp = await self.get_request_response(url, method=method,
							params=params,
							data=data,
							jd=jd,
							headers=headers,
							**kw)
		if resp.status==200:
			async for d in self.response_generator(url, resp):
				yield d
			return 
		msg = f'http error({resp.status}, {url=},{params=}, {data=}, {jd=})'
		exception(msg)
		raise HttpError(resp.status, msg)

	async def get(self,url,**kw):
		return self.request(url, 'GET', **kw)

	async def post(self,url, **kw):
		return self.request(url, 'POST', **kw)

class JsonHttpAPI:
	def __init__(self, env={}, socks5_proxy_url=None):
		self.env = env
		self.te = MyTemplateEngine([], env=env)
		self.hc = HttpClient(socks5_proxy_url=socks5_proxy_url)
		
	async def stream_func(self, chunk):
		debug(f'{chunk=}')
		d = self.chunk_buffer + chuck
		a, b = d.split('\n', 1)
		self.chunk_buffer = b
		if self.resptmpl:
			ns1 = json.loads(a)
			a = self.te.renders(self.resptmpl, ns1)
		if self.user_stream_func:
			jd = json.loads(a)
			await self.user_stream_func(jd)
			
	async def chunk_handle(self, chunk, chunk_lead, chunk_end):
		return chunk

	async def __call__(self,  url, method='GET', ns={},
					headerstmpl=None,
					paramstmpl=None,
					datatmpl=None,
					chunk_leading=None,
					chunk_end="[done]",
					resptmpl=None):
		headers = None
		self.chunk_buffer = ''
		ns1 = self.env.copy()
		ns1.update(ns)
		if headerstmpl:
			headers = json.loads(self.te.renders(headerstmpl, ns1))
			info(f'{headers=},{ns=}, {headerstmpl=}')
		params = None
		if paramstmpl:
			params = json.loads(self.te.renders(paramstmpl, ns1))
		data = None
		stream = False
		if datatmpl:
			datadic = json.loads(self.te.renders(datatmpl, ns1))
			stream = atadic.get('stream', False)
			data = json.dumps(datadic, ensure_ascii=False)
		hc = HttpClient()
		async for d in self.hc(url, method=method, 
						stream=stream,
						headers=headers,
						params=params,
						data=data):
			if stream:
				d = self.chunk_handle(d, chunk_leading, chunk_end)
			if resptmpl:
				dic = json.loads(d)
				ns1.update(dic)
				d = self.te.renders(resptmpl, ns1)
			yield d

	async def call(self, url, method='GET', ns={}, 
					stream_func=None,
					headerstmpl=None, 
					paramstmpl=None,
					datatmpl=None,
					chunk_leading=None,
					chunk_end="[done]",
					resptmpl=None):
		self.user_stream_func = stream_func
		self.chunk_leading = chunk_leading
		self.chunk_end = chunk_end
		self.chunk_buffer = ''
		self.resptmpl =resptmpl
		headers = None
		ns1 = self.env.copy()
		ns1.update(ns)
		if headerstmpl:
			headers = json.loads(self.te.renders(headerstmpl, ns1))
			info(f'{headers=},{ns=}, {headerstmpl=}')
		params = None
		if paramstmpl:
			params = json.loads(self.te.renders(paramstmpl, ns1))
		data = None
		if datatmpl:
			datadic = json.loads(self.te.renders(datatmpl, ns1))
			data = json.dumps(datadic, ensure_ascii=False)
			"""
			data = FormData()
			for k,v in datadic.items():
				data.add_field(k, v)
			headers['Content-Type'] = 'multipart/form-data'
			"""
			info(f'{data=},{ns=}, {headers=}')
		if stream_func:
			resp = await self.hc.request(url, method=method, headers=headers,
						stream_func=stream_func,
						params=params,
						data=data)
		else:
			resp = await self.hc.request(url, method=method, headers=headers,
						response_type=RESPONSE_JSON,
						params=params,
						data=data)
		ret = resp
		if resptmpl:
			ns1 = self.env.copy()
			ns1.update(resp)
			rets = self.te.renders(resptmpl, ns1)
			ret = json.loads(rets)
		return ret

if __name__ == '__main__':
	async def main():
		hc = HttpClient(socks5_proxy_url='socks5://localhost:1086')
		async for d in hc('https://www.baidu.com'):
			print(d)
		r = await hc.request('https://www.google.com')
		print(r)
		await hc.close()
	loop = asyncio.new_event_loop()
	loop.run_until_complete(main())

