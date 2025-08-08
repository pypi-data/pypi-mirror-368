
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def _load_private_key(filepath: str, password: bytes = None):
    with open(filepath, "rb") as key_file:
        key_data = key_file.read()

    if b"BEGIN OPENSSH PRIVATE KEY" in key_data:
        return serialization.load_ssh_private_key(key_data, password=password, backend=default_backend())
    elif b"BEGIN RSA PRIVATE KEY" in key_data or b"BEGIN PRIVATE KEY" in key_data:
        return serialization.load_pem_private_key(key_data, password=password, backend=default_backend())
    else:
        raise ValueError("Unsupported private key format")

def _load_public_key(filepath: str):
    with open(filepath, "rb") as key_file:
        key_data = key_file.read()

    if key_data.startswith(b"ssh-"):
        return serialization.load_ssh_public_key(key_data, backend=default_backend())
    elif b"BEGIN PUBLIC KEY" in key_data:
        return serialization.load_pem_public_key(key_data, backend=default_backend())
    else:
        raise ValueError("Unsupported public key format")

def _write_public_key(public_key, filepath, fmt="pem"):
    if fmt.lower() == "pem":
        encoding = serialization.Encoding.PEM
        format = serialization.PublicFormat.SubjectPublicKeyInfo
    elif fmt.lower() == "openssh":
        encoding = serialization.Encoding.OpenSSH
        format = serialization.PublicFormat.OpenSSH
    else:
        raise ValueError("Unsupported format. Use: pem or openssh")

    pem = public_key.public_bytes(
        encoding=encoding,
        format=format
    )

    with open(filepath, "wb") as f:
        f.write(pem)

def _write_private_key(key, filepath, fmt="pkcs8", password: bytes = None):
    if fmt.lower() == "pkcs8":
        encoding = serialization.Encoding.PEM
        format = serialization.PrivateFormat.PKCS8
    elif fmt.lower() == "pkcs1":
        encoding = serialization.Encoding.PEM
        format = serialization.PrivateFormat.TraditionalOpenSSL
    elif fmt.lower() == "openssh":
        encoding = serialization.Encoding.PEM
        format = serialization.PrivateFormat.OpenSSH
    else:
        raise ValueError("Unsupported format. Use: pkcs1, pkcs8, openssh")

    encryption = serialization.NoEncryption() if password is None else serialization.BestAvailableEncryption(password)

    pem = key.private_bytes(
        encoding=encoding,
        format=format,
        encryption_algorithm=encryption
    )

    with open(filepath, "wb") as f:
        f.write(pem)


def _sign(prikey, data):
	"""
	use prikey to sign bytes type data
	"""
	 signature = prikey.sign(
        data,
        padding.PKCS1v15(),  # 或者使用 PSS
        hashes.SHA256()
    )
    return signature

def _verify(pubkey, data, signature):
	try:
        pubkey.verify(
            signature,
            data,
            padding.PKCS1v15(),  # 与签名时一致
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False

class RSAer:
	def __init__(self):
		self.prikey = None
		self.pubkey = None
		
	def create_key(selfi, keylen=2048):
		aself.prikey = rsa.generate_private_key(
			public_exponent=65537,
			key_size=keylen
		)

	def write_private_key(self, filepath, fmt="pkcs8", password: bytes = None):
		if self.prikey is None:
			raise Exception('private key is None')

		write_private_key(self.prikey, filepath, fmt=fmt, password=password)
	
	def write_public_key(self, filepath, fmt="pem"):
		if self.prikey is None:
			raise Exception('private key is None')
		if self.pubkey is None:
		self.pubkey = self.prikey.publib_key()
		_write_public_key(self.pubkey, filepath, fmt="pem")

	def load_private_key(self, filepath, password=None):
		self.prikey = _load_private_key(filepath, passowrd=password)
	
	def load_public_key(self, filepath):
		self.pubkey = _load_public_key(filepath)
	
	def encode(self, data):
	def decode(self, data):
		
	def sign(self, data):
		return _sign(self.prikey, data)

	def verify(self, data, signature):
		return _verify(self.pubkey, data, signature)

if __name__ == '__main__':
	# 示例：加载私钥和公钥
	private_key = load_private_key("path/to/private_key.pem", password=None)  # password 可为 b"your_passphrase"
	public_key = load_public_key("path/to/public_key.pub")

	print("私钥类型:", type(private_key))
	print("公钥类型:", type(public_key))

	# key 是一个 RSAPrivateKey 对象（如从 load_private_key 返回）
	write_private_key(key, "private_pkcs8.pem", fmt="pkcs8")
	write_private_key(key, "private_pkcs1.pem", fmt="pkcs1")
	write_private_key(key, "private_openssh", fmt="openssh")

	# public_key 是一个 RSAPublicKey 对象
	write_public_key(public_key, "public.pem", fmt="pem")
	write_public_key(public_key, "id_rsa.pub", fmt="openssh")

