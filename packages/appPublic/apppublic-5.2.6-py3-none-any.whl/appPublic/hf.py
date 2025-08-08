import requests
from huggingface_hub import configure_http_backend, get_session

def hf_socks5proxy(proxies={
				"http": "socks5h://127.0.0.1:1086", 
				"https": "socks5h://127.0.0.1:1086"
				}):
	# Create a factory function that returns a Session with configured proxies
	print(f'proxies={proxies}')
	def backend_factory() -> requests.Session:
		session = requests.Session()
		session.proxies = proxies
		print(f'socks5 proxy set {proxies=}')
		return session

	# Set it as the default session factory
	configure_http_backend(backend_factory=backend_factory)

if __name__ == '__main__':
	hf_socks5proxy()
