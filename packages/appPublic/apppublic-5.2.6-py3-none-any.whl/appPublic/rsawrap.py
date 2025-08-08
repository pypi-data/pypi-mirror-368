import rsa

class RSA:
	
	def __init__(self, keylength=4096, coding='iso8859'):
		self.coding = coding
		self.keylength = keylength
		
	def write_privatekey(self,private_key,fname,password=None):
		bd = private_key.save_pkcs1()
		with open(fname, 'wb') as f:
			f.write(bd)

	def publickeyText(self,public_key):
		bd = public_key.save_pkcs1()
		return bd.decode(self.coding)

	def write_publickey(self,public_key,fname):
		bd = public_key.save_pkcs1()
		with open(fname, 'wb') as f:
			f.write(bd)

	def read_privatekey(self,fname,password=None):
		with open(fname, 'rb') as pf:
			kd = pf.read()
			return rsa.PrivateKey.load_pkcs1(kd)

	def publickeyFromText(self,text):
		bd = text.encode(self.coding)
		return rsa.PublicKey.load_pkcs1(bd)

	def read_publickey(self,fname):
		with open(fname, 'rb') as pf:
			kd = pf.read()
			return rsa.PublicKey.load_pkcs1(kd)

	def create_privatekey(self, keylength=4096):
		_, prik = rsa.newkeys(keylength)
		return prik

	def create_publickey(self,private_key):
		return rsa.PublicKey(private_key.n, private_key.e)

	def encode_bytes(self, public_key, bdata):
		return rsa.encrypt(bdata, public_key)

	def encode(self,public_key,text):
		bdata = text.encode(self.coding)
		bc = self.encode_bytes(public_key, bdata)
		return bc.decode(self.coding)

	def decode_bytes(self, private_key, bdata):
		return rsa.decrypt(bdata, private_key)

	def decode(self,private_key,cipher):
		bc = cipher.encode(self.coding)
		bd = self.decode_bytes(private_key, bc)
		return bd.decode(self.coding)

	def sign_bdata(self, private_key, data_to_sign):
		return rsa.sign(data_to_sign, private_key, 'SHA-1')

	def sign(self,private_key,message):
		bd = message.encode(self.coding)
		bs = self.sign_bdata(private_key, bd)
		return bs.decode(self.coding)

	def check_sign_bdata(self, public_key, bdata, sign):
		try:
			r = rsa.verify(bdata, sign, public_key)
			if r == 'SHA-1':
				return True
			print(f'verify()={r}')
			return False
		except Exception as e:
			print(f'check_sign_bdata() raise Exception{e}')
			return False


	def check_sign(self,public_key,plain_text,signature):
		bd = plain_text.encode(self.coding)
		bs = signature.encode(self.coding)
		return self.check_sign_bdata(public_key, bd, bs)


if __name__ == '__main__':
	import os
	prikey1_file = os.path.join(os.path.dirname(__file__),'..','test', 'prikey1.rsa')
	r = RSA()
	mpri = r.create_privatekey(2048)
	mpub = r.create_publickey(mpri)
	
	zpri = r.create_privatekey(2048)
	zpub = r.create_publickey(zpri)
	
	l = 100
	while True:
		text = 'h' * l
		cipher = r.encode(mpub,text)
		ntext = r.decode(mpri,cipher)
		print('textlen=', l, 'encode text=', text, \
				'decode result=', ntext,
				'cyber size=', len(cipher),
				'check if equal=', text==ntext)
		signature = r.sign(zpri,text)
		check = r.check_sign(zpub,text,signature)
		print('sign and verify=',len(signature),check)
		l += 1
