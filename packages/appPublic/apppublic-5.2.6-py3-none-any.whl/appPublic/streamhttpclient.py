#!/Users/ymq/p3.12/bin/python

from traceback import format_exc
import aiohttp
import asyncio
from aiohttp_socks import ProxyConnector
from pathlib import Path
import certifi
import ssl
import os
from appPublic.log import exception, debug

async def liner(async_gen):
	remainer = b''
	async for chunk in async_gen:
		# chunk = chunk.decode('utf-8')
		d = remainer + chunk
		lst = d.split(b'\n')
		cnt = len(lst)
		for c in range(cnt-1):
			yield lst[c]
		remainer = lst[-1]
	if remainer != b'':
		yield remainer

def get_non_verify_ssl():
	ssl_context = ssl.create_default_context(cafile=certifi.where())
	ssl_context.check_hostname = False
	ssl_context.verify_mode = ssl.CERT_NONE
	return ssl_context

class StreamHttpClient:
	def __init__(self, socks5_url="socks5://127.0.0.1:1086"):
		home = os.path.expanduser("~")
		self.socks_urls_file = Path(f'{home}/.socksurls.txt')
		self.socks5_url = socks5_url
		self.socks_urls = set(self._load_socks_urls())
		self.ssl_context = ssl.create_default_context(cafile=certifi.where())

	def _load_socks_urls(self):
		if self.socks_urls_file.exists():
			return [line.strip() for line in self.socks_url_file.read_text().splitlines() if line.strip()]
		return []

	def _save_socks_url(self, url):
		if url not in self.socks_urls:
			self.socks_urls.add(url)
			with self.socks_url_file.open("a") as f:
				f.write(url + "\n")

	async def request(self, method, url, *,
					  headers=None,
					  params=None,
					  data=None,
					  json=None,
					  files=None,
					  chunk_size=1024, **kw):
		ret = b''
		async for chunk in self.__call__(method, url, headers=headers,
					  params=params,
					  data=data,
					  json=json,
					  files=files,
					  chunk_size=1024, **kw):
			ret += chunk
		return ret

	async def __call__(self, method, url, *,
					  headers=None,
					  params=None,
					  data=None,
					  json=None,
					  files=None,
					  chunk_size=1024, **kw):
		"""
		Makes an HTTP request and yields response chunks (streamed).
		"""
		use_socks = url in self.socks_urls
		try:
			if use_socks:
				debug(f"🔁 Using SOCKS5 directly for: {url}")
				async for chunk in self._request_with_connector(
					method, url,
					headers=headers, params=params, data=data,
					json=json, files=files,
					use_socks=True, chunk_size=chunk_size, **kw
				):
					yield chunk
			else:
				debug(f"🌐 Trying direct request: {url}")
				async for chunk in self._request_with_connector(
					method, url,
					headers=headers, params=params, data=data,
					json=json, files=files,
					use_socks=False, chunk_size=chunk_size, **kw
				):
					yield chunk
		except Exception as e:
			if use_socks:
				exception(f"❌ SOCKS5 request failed: {e},{format_exc()}")
				return
			debug(f"❌ Direct request failed: {e}")
			debug("🧦 Retrying with SOCKS5 proxy...")
			try:
				async for chunk in self._request_with_connector(
					method, url,
					headers=headers, params=params, data=data,
					json=json, files=files,
					use_socks=True, chunk_size=chunk_size, **kw
				):
					self._save_socks_url(url)
					yield chunk
			except Exception as e2:
				exception(f"❌ SOCKS5 request also failed: {e2},{format_exc()}")

	async def _request_with_connector(self, method, url,
									  headers=None, params=None, data=None,
									  json=None, files=None,
									  use_socks=False, 
									  chunk_size=1024,
									  **kw):
		connector = ProxyConnector.from_url(self.socks5_url) if use_socks else None

		async with aiohttp.ClientSession(connector=connector) as session:
			req_args = {k:v for k,v in kw.items() if k not in ['verify']}
			ssl_context = self.ssl_context
			if 'verify' in kw.keys() and kw.get('verify') == False:
				ssl_context = get_non_verify_ssl()
			else:
				ssl_context = self.ssl_context

			req_args.update({
				"headers": headers,
				"params": params,
				"ssl": ssl_context,
			})

			if files:
				form = aiohttp.FormData()

				if isinstance(data, dict):
					for k, v in data.items():
						form.add_field(k, str(v))

				for name, file_info in files.items():
					form.add_field(name, *file_info)

				req_args["data"] = form
			else:
				if json is not None:
					req_args["json"] = json
				else:
					req_args["data"] = data

			async with session.request(method, url, **req_args) as response:
				response.raise_for_status()
				async for chunk in response.content.iter_chunked(chunk_size):
					yield chunk

if __name__ == '__main__':
	import asyncio
	import sys
	
	async def main():
		if len(sys.argv) > 1:
			prompt = sys.argv[1]
		else:
			prompt = 'who are you'
		hc = StreamHttpClient()
		url = 'https://www.baidu.com'
		x = await hc.request('GET', url, verify=False, timeout=2)
		print(x)

	asyncio.new_event_loop().run_until_complete(main())

