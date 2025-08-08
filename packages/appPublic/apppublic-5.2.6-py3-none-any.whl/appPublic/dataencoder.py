try:
	import ujson as json
except:
	import json
from appPublic.rsawrap import RSA
from appPublic.rc4 import RC4
from appPublic.uniqueID import getID

# import brotli
import zlib
import struct

DATA_TYPE_BYTES = 1
DATA_TYPE_STR = 2
DATA_TYPE_JSON = 3

class DataEncoder:
	"""
	security data packing - unpacking object
	packs data:
	encode data with random key's rc4 crypt algorithm, 
	encode rc4's key with receiver's public key
	sign data with sender's private key
	packs data using struct in follows order
	0: data format(18 bytes)
	1. datatype(c)
	2. encoded data(length=len(d))
	3. encoded_rc4key(length=len(k))
	4. sign(signs from (0+1+2+3) data) (length=len(s))
	5. compress data and return compressed dta
	return packed data
	unpacks data:
	0. decompress data
	1. get 18 bytes fmt data, erase tails b'\x00'
	2. using fmt to unpack data[18:]
	3. verify sign
	4. decode k
	5. decode data usig decoded k with rc4 algorithm
	6. convert data type to origin data type
	7. return converted data
	"""
	def __init__(self, myid, func_get_peer_pubkey, private_file=None):
		self.myid = myid
		self.func_get_peer_pubkey = func_get_peer_pubkey
		self.public_keys = {}
		self.private_file = private_file
		self.rsa = RSA()
		self.rc4 = RC4()
		if self.private_file:
			self.private_key = self.rsa.read_privatekey(self.private_file)
		else:
			self.private_key = self.rsa.create_privatekey()
		self.public_key = self.rsa.create_publickey(self.private_key)

	def identify_datatype(self, data):
		if isinstance(data, bytes):
			return DATA_TYPE_BYTES, data
		if isinstance(data, str):
			return DATA_TYPE_STR, data.encode('utf-8')
		data = json.dumps(data).encode('utf-8')
		return DATA_TYPE_JSON, data

	def my_text_publickey(self):
		return self.rsa.publickeyText(self.public_key)

	def exist_peer_publickeys(self, peer_id):
		return True if self.public_keys.get(peer_id, False) else False

	def set_peer_pubkey(self, peer_id, pubkey):
		self.public_keys[peer_id] = pubkey

	def get_peer_text_pubkey(self, peer_id):
		pk = self.get_peer_pubkey()
		txtpk = self.rsa. publickeyText(pk)
		return txtpk

	def set_peer_text_pubkey(self, peer_id, text_pubkey):
		pk = self.rsa.publickeyFromText(text_pubkey)
		self.set_peer_pubkey(peer_id, pk)

	def get_peer_pubkey(self, peer_id):
		pubkey = self.public_keys.get(peer_id)
		if not pubkey:
			try:
				self.func_get_peer_pubkey(peer_id)
			except:
				raise Exception('Can not get peer public key(%s)')
			pubkey = self.public_keys.get(peer_id)
		return pubkey

	def pack(self, peer_id, data, uncrypt=False):
		t, d = self.identify_datatype(data)
		if uncrypt:
			return zlib.compress(b'\x00' * 18 + \
						bytes(chr(t),'utf-8') + \
						d)
		pk = self.get_peer_pubkey(peer_id)
		d, k = self.encode_data(pk, d)
		f = 'b%05ds%03ds' % (len(d), len(k))
		f1 = f + '256s'
		pd1 = struct.pack('18s', f1.encode('utf-8'))
		pd2 = struct.pack(f, t, d, k)
		pd = pd1 + pd2
		s = self.sign_data(pd)
		pd += s
		self.pack_d = [t,d,k,s]
		origin_len = len(pd)
		pd = zlib.compress(pd)
		return pd

	def unpack(self, peer_id, data):
		data = zlib.decompress(data)
		if data[:18] == b'\x00' * 18:
			data = data[18:]
			t = ord(chr(data[0]))
			d = data[1:]
			if t == DATA_TYPE_BYTES:
				return d
			d = d.decode('utf-8')
			if t == DATA_TYPE_STR:
				return d
			return json.loads(d)

		org_data = data
		pk = self.get_peer_pubkey(peer_id)
		f = data[:18]
		while f[-1] == 0 and len(f) > 0:
			f = f[:-1]
		f = f.decode('utf-8')
		data = data[18:]
		t, d, k, s = struct.unpack(f, data)
		self.unpack_d = [t,d,k,s]
		data1 = org_data[:org_data.index(s)]
		if not self.verify_sign(data1, s, pk):
			raise Exception('data sign verify failed')
		data = self.decode_data(d, k)
		if t == DATA_TYPE_BYTES:
			return data
		if t == DATA_TYPE_STR:
			return data.decode('utf-8')
		return json.loads(data)

	def encode_data(self, peer_pubkey, data):
		key = getID()
		if isinstance(key, str):
			key = key.encode('utf-8')
		ctext = self.rc4.encode_bytes(data, key)
		encoded_key = self.rsa.encode_bytes(peer_pubkey, key)
		return ctext, encoded_key

	def sign_data(self, data):
		return self.rsa.sign_bdata(self.private_key, data)

	def decode_data(self, data, encoded_key):
		key = self.rsa.decode_bytes(self.private_key, encoded_key)
		return self.rc4.decode_bytes(data, key)

	def verify_sign(self, data, sign, peer_pubkey):
		return self.rsa.check_sign_bdata(peer_pubkey, data, sign)

def quotedstr(s):
	def conv(c):
		if c == '"':
			return '\\"'
		if c == '\n':
			return '\\n'
		return c
	x = [ conv(c) for c in s ]
	return ''.join(x)

