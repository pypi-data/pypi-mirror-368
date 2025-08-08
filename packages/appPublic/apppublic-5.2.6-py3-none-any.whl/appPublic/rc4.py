# -*- coding: utf-8 -*-  
import time
import datetime
import random, base64  
from hashlib import sha1  
 
class RC4:
	def __init__(self,data_coding='utf8'):
		self.bcoding = 'iso-8859-1'
		self.dcoding = data_coding
		self.salt = b'AFUqx9WZuI32lnHk'
	
	def _crypt(self,data,key):
		"""RC4 algorithm return bytes"""
		x = 0  
		box = [i for i in range(256) ]
		for i in range(256):  
			x = (x + box[i] + key[i % len(key)]) % 256  
			box[i], box[x] = box[x], box[i]  
		x = y = 0  
		out = []  
		for char in data:
			x = (x + 1) % 256  
			y = (y + box[x]) % 256  
			box[x], box[y] = box[y], box[x]  
			out.append(chr(char ^ box[(box[x] + box[y]) % 256]))  

		return ''.join(out).encode(self.bcoding) 
  
	def encode_bytes(self, bdata, key):
		a = sha1(key + self.salt)
		k = a.digest()
		data = self.salt + self._crypt(bdata, k)
		return data

	def encode(self,data, key,encode=base64.b64encode, salt_length=16):  
		"""RC4 encryption with random salt and final encoding"""  
		if type(data)==type(''):
			data = data.encode(self.dcoding)
		key = key.encode(self.bcoding)
		code = self.encode_bytes(data, key)
		if encode:  
			code = encode(code)
		return code.decode(self.dcoding)
		return code

	def decode_bytes(self, data, key):
		salt_length = 16
		salt = data[:salt_length]
		a = sha1(key + self.salt)
		k = a.digest() #.decode('iso-8859-1')
		r = self._crypt(data[salt_length:], k)
		return r

	def decode(self,data, key,decode=base64.b64decode, salt_length=16):  
		"""RC4 decryption of encoded data"""  
		if type(data)==type(''):
			data = data.encode(self.dcoding)
		key = key.encode(self.bcoding)
		if decode:  
			data = decode(data)  
		r = self.decode_bytes(data, key)
		return r.decode(self.dcoding)

class KeyChain(object):
	def __init__(self, seed_str, crypter=None, keylen=23, period=600, threshold=60, time_delta=0):
		self.seed_str = seed_str
		if isinstance(self.seed_str, str):
			self.seed_str = self.seed_str.encode('utf-8')
		self.period = int(period)
		self.threshold = int(threshold)
		self.crypter = crypter
		self.time_delta = time_delta
		if crypter is None:
			self.crypter = RC4()
		self.keylen = keylen
		self.keypool = {
		}
		delta = datetime.timedelta(0)
		self.timezone = datetime.timezone(delta, name='gmt')
	
	def get_timestamp(self):
		ts = int(time.time()) - self.time_delta
		return ts

	def is_near_bottom(self, indicator=None):
		ts = self.get_timestamp()
		i = indicator
		if i is None:
			i = self.get_indicator(ts)
		if i + self.threshold > ts:
			return True
		return False

	def is_near_top(self, indicator=None):
		ts = self.get_timestamp()
		i = indicator
		if i is None:
			i = self.get_indicator(ts)
		if i + self.period - self.threshold < ts:
			return True
		return False

	def get_indicator(self, ts=None):
		if ts is None:
			ts = self.get_timestamp()
		return int(ts / self.period) * self.period
		
	def genKey(self, indicator):
		vv = indicator
		if self.keypool.get(vv):
			return self.keypool[vv]
		v = vv
		k1 = 0
		k = ''
		m = len(self.seed_str)
		while k1 < self.keylen:
			j = v % self.keylen
			v = v - (j + k1) * m + self.keylen
			k = k + chr(self.seed_str[j])
			k1 += self.threshold / 2
		key = k.encode('utf-8')
		self.keypool[vv] = key
		dates = [ d for d in self.keypool.keys() ]
		for d in dates:
			if d < indicator - self.period:
				del self.keypool[d]
		return key

	def encode(self, text):
		bdata = text.encode('utf-8')
		return self.encode_bytes(bdata)

	def encode_bytes(self, bdata):
		indicator = self.get_indicator()
		key = self.genKey(indicator)
		data = key + bdata
		return self.crypter.encode_bytes(data, key)

	def _decode(self, data, key):
		d = self.crypter.decode_bytes(data, key)
		if d[:len(key)] == key:
			return d[len(key):]
		return None

	def decode_bytes(self, data):
		indicator = self.get_indicator()
		key = self.genKey(indicator)
		d = self._decode(data, key)
		if d is not None:
			return d

		if self.is_near_bottom(indicator):
			indicator -= self.period
			key = self.genKey(indicator)
			return self._decode(data, key)
			
		if self.is_near_top(indicator):
			indicator += self.period
			key = self.genKey(indicator)
			return self._decode(data, key)
		return None
  
	def decode(self, data):
		d = self.decode_bytes(data)
		if d is None:
			return None
		return d.decode('utf-8')

pwdkey = 'ytguiojbhvhbnkl'
def password(pwdtxt, key=pwdkey):
	rc = RC4()
	code = rc.encode(pwdtxt, key)
	t = rc.decode(code, key)
	if (t == pwdtxt):
		return code
	else:
		return None

def unpassword(code, key=pwdkey):
	rc = RC4()
	t = rc.decode(code, key)
	return t
	
"""
if __name__ == '__main__':
	import sys
	if len(sys.argv) > 1:
		print(password(sys.argv[1]))
		sys.exit(0)
	ps = [
		'45dr6tcfyvguh',
		'ft7gy8uh9ij0',
		'opiluykhcgjfncm'
	]
	for p in ps:
		print(password(p))
"""

if __name__=='__main__':  
	# 需要加密的数据长度没有限制 
	# 密钥 

	data=b"231r3 feregrenerjk gkht324g8924gnfw k;ejkvwkjerv"
	key = b'123456'  
	rc4 = RC4()
	kc = KeyChain('in the heaven, we are equal', rc4)
	
	print(data)
	# 加码  
	encoded_data = kc.encode_bytes(data)  
	print(encoded_data,len(encoded_data) )
	# 解码  
	decoded_data = kc.decode_bytes(encoded_data)  
	print(data, decoded_data, decoded_data==data)
