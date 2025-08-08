from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
"""
use AES ECBmode to encrypt and decrype
"""

def pad(data: bytes) -> bytes:
	padder = padding.PKCS7(128).padder()  # AES 块大小是 128 bits
	return padder.update(data) + padder.finalize()

def unpad(data: bytes) -> bytes:
	unpadder = padding.PKCS7(128).unpadder()
	return unpadder.update(data) + unpadder.finalize()

def aes_encrypt_ecb(key: bytes, plaintext: str) -> bytes:
	
	cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
	encryptor = cipher.encryptor()
	padded_data = pad(plaintext.encode())
	return encryptor.update(padded_data) + encryptor.finalize()

def aes_decrypt_ecb(key: bytes, ciphertext: bytes) -> str:
	cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
	decryptor = cipher.decryptor()
	padded_plain = decryptor.update(ciphertext) + decryptor.finalize()
	return unpad(padded_plain).decode()


if __name__ == '__main__':
	key = b'67t832ufbj43riu8'
	o = 'this is s test string'
	b = aes_encrypt_ecb(key, o)
	t = aes_decrypt_ecb(key, b)
	print(f'{o=},{b=},{t=}')
