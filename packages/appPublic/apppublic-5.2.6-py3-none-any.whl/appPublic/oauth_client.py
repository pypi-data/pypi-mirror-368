import json
from appPublic.httpclient import HttpClient, RESPONSE_TEXT, RESPONSE_JSON, RESPONSE_BIN,RESPONSE_FILE, RESPONSE_STREAM, HttpError
from appPublic.argsConvert import ArgsConvert
from appPublic.dictObject import DictObject

class OAuthClient:
	"""
	OauthClient is a http(s) client for request a api annouce by other
	it send https request and get back a json data
	we can check the response json data to check if the call is success or failed
	desc has the following format
	{
		"data": predefined data, and if nessory, you can add to new data to it
		"method_name":{
			"url"
			"method",
			"headers",
			"params":arguments will appended to url with ?a=a&b=b...
			"data":data will send in the request body, json format
			"resp":[
				{
					"name":
					"converter":default none, if not, convert response data first before set the returen data
					"keys":resposne json data keys to achieve data
				}
			]
			"error_if":{
				"keys":
				"op",
				"value"
			}
		}
	}
	return:
		if error:
			return {
				"status":"error",
				"code":code returned by server
				"message":"message returned by server
			}
		else:
			return {
				"status":"ok",
				"data":...
			}

	"""
	def __init__(self, desc, converters={}):
		assert desc.get('data')
		self.desc = desc
		self.data = desc.get('data')
		self.converters = converters
		self.ac = ArgsConvert('${', '}')
	
	def setup_req_data(self, data=[], ns={}):
		d = {}
		if data is None:
			return None
		for h in data:
			d1 = self.setup_req_kv(h, ns)
			d.update(d1)
		if d == {}:
			return None
		return d
	
	def setup_req_kv(self, d, ns):
		rd = {
			d.name:d.value
		}
		nd = self.datalize(rd, ns)
		if d.converter:
			f = self.converters.get(d.converter)
			if f:
				nd[d.name] = f(nd.get(d.name))
		return nd

	async def __call__(self, host, mapi, params):
		if not self.desc.get(mapi):
			raise Exception(f'{mapi} not defined')
		self.api = self.desc[mapi]
		if not self.api:
			return {
				"status":"error",
				"code":'9999',
				"message":f"{mapi} not defined"
			}
		path = self.datalize(self.api.path, params)
		url = host + path
		method = self.api.get('method', 'GET')
		myheaders =  self.setup_req_data(self.api.headers, params)
		myparams =  self.setup_req_data(self.api.params, params)
		mydata =  self.setup_req_data(self.api.data, params)
		response_type =  RESPONSE_JSON
		hc = HttpClient()
		print(f'{url=}, {method=}, {myparams=}, {mydata=}, {myheaders=}')
		resp_data = None
		try:
			resp_data = await hc.request(url, method, response_type=response_type,
								params=None if not myparams else myparams,
								data=None if not mydata else mydata,
								headers=myheaders)
			resp_data = DictObject(**resp_data)
			print(resp_data)
		except HttpError as e:
			return {
				"status":"error",
				"code":e.code,
				"message":e.msg
			}
			
		if resp_data is None:
			return {
				"status":"error",
				"code":None,
				"message":"https error"
			}
		err = self.check_if_error(resp_data)
		if err:
			return err
		return self.setup_return_data(resp_data)
		
	def datalize(self, dic, data={}):
		mydata = self.data.copy()
		mydata.update(data)
		s1 = self.ac.convert(dic, mydata)
		return s1
	
	def get_resp_data(self, resp, keys, converter=None):
		d = resp.get_data_by_keys(keys)
		if converter:
			f = self.converters.get(converter)
			if f:
				d = f(d)
		return d

	def setup_return_data(self, resp):
		data = {}
		if not self.api.resp:
			return {
				'status':'ok',
				'data':{}
			}

		for desc in self.api.resp:
			k = desc.name
			v = self.get_resp_data(resp, desc.resp_keys, desc.converter)
			data[k] = v
		return {
			"status":"ok",
			"data":data
		}

	def check_if_error(self, resp):
		if not self.api.error_if:
			return None
		ei = self.api.error_if
		v = resp.get_data_by_keys(ei.error_keys)
		v1 = ei.value
		if ei.converter:
			f = self.converters.get(ei.converter)
			if f:
				v = f(v)
		if not ei.op:
			ei.op = '=='
		print(f'{ei.keys=},{v=}, {v1=}, {ei.op=}{v==v1}, {resp.base_resp.status_code=}')
		if (ei.op == '==' and v == v1) or (ei.op == '!=' and v != v1):
			print(f'{v=}, {v1=}, {ei.op=}{v==v1}')
			code = None
			message = None
			if ei.code_keys:
				code = resp.get_data_by_keys(ei.code_keys)
			if ei.msg_keys:
				message = resp.get_data_by_keys(ei.msg_keys)
			return {
				"status":"error",
				"code":code,
				"message":message
			}
		print(f'check_if_error ok:{v=}, {v1=}, {ei.op=}{v==v1}')
		return None		

	def set_data(self, resp_data, data_desc):
		for dd in data_desc:
			f = dd['field']
			n = dd['name']
			if  resp_data.get(f):
				self.data[n] = resp_data[f]
	
