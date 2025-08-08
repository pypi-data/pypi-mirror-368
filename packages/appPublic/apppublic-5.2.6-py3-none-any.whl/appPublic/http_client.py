import requests

class NeedLogin(Exception):
	pass

class InsufficientPrivilege(Exception):
	pass

class HTTPError(Exception):
	def __init__(self,resp_code,url=None):
		self.resp_code = resp_code
		self.url = url
		Exception.__init__(self)

	def __expr__(self):
		return f'{self.url}:{self.resp_code}'

	def __str__(self):
		return f'{self.url}:{self.resp_code}'

hostsessions = {}

class Http_Client:
	def __init__(self):
		self.s = requests.Session()
		self.s.verify = False
		self.s.hooks['response'].append(self.response_handler)

	def prepped_handler(self, prepped):
		pass

	def response_handler(self, resp, *args, **kw):
		return resp
		
	def url2domain(self,url):
		parts = url.split('/')[:3]
		pre = '/'.join(parts)
		return pre

	def _webcall(self,url,method="GET",
					params={},
					files={},
					headers={},
					stream=False):
		domain = self.url2domain(url)
		sessionid = hostsessions.get(domain,None)
		if sessionid:
			headers.update({'session':sessionid})
		
		if method in ['GET']:
			req = requests.Request(method,url,
					params=params,headers=headers)
		else:
			req = requests.Request(method,url,
					data=params,files=files,headers=headers)
		prepped = self.s.prepare_request(req)
		self.prepped_handler(prepped)
		resp = self.s.send(prepped)
		if resp.status_code == 200:
			h = resp.headers.get('Set-Cookie',None)
			if h:
				sessionid = h.split(';')[0]
				hostsessions[domain] = sessionid

		if resp.status_code == 401:
			print('NeedLogin:',url)
			raise NeedLogin

		if resp.status_code == 403:
			raise InsufficientPrivilege

		if resp.status_code != 200:
			print('Error', url, method, 
					params, resp.status_code,
					type(resp.status_code))
			raise HTTPError(resp.status_code,url)
		return resp

	def webcall(self,url,method="GET",
				params={},
				files={},
				headers={},
				stream=False):
		resp = self._webcall(url,method=method,
				params=params,
				files=files,
				headers=headers,
				stream=stream)
		if stream:
			return resp
		try:
			data = resp.json()
			if type(data) != type({}):
				return data
			status = data.get('status',None)
			if status is None:
				return data
			if status == 'OK':
				return data.get('data')
			return data
		except:
			return resp.text
		
	def __call__(self,url,method="GET",
				params={},
				headers={},
				files={},
				stream=False):
		return self.webcall(url, method=method,
						params=params, files=files, 
						headers=headers, stream=stream)

	def get(self, url, params={}, headers={}, stream=False):
		return self.__call__(url,method='GET',params=params,
				headers=headers, stream=stream)
	def post(self, url, params={}, headers={}, files={}, stream=False):
		return self.__call__(url,method='POST',params=params, files=files,
				headers=headers, stream=stream)

	def put(self, url, params={}, headers={}, stream=False):
		return self.__call__(url,method='PUT',params=params,
				headers=headers, stream=stream)

	def delete(self, url, params={}, headers={}, stream=False):
		return self.__call__(url,method='DELETE',params=params,
				headers=headers, stream=stream)

	def option(self, url, params={}, headers={}, stream=False):
		return self.__call__(url,method='OPTION',params=params,
				headers=headers, stream=stream)
	
