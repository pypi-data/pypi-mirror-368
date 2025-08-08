import os
import sys
from requests import get
from bs4 import BeautifulSoup
from appPublic.http_client import Http_Client
from appPublic.sockPackage import get_free_local_addr
public_headers = {
	"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3100.0 Safari/537.36"
}

def get_outip():
	ip = get('https://api.ipify.org').content.decode('utf8')
	return ip

def ipip(ip=None):
	# ipip.net
	if ip is None:
		ip = get_outip()
	api= f"http://freeapi.ipip.net/{ip}"
	hc = Http_Client()
	r= hc.get(api, headers=public_headers)
	return {
		'country':r[0],
		'city':r[2]
	}

def ipapi_co(ip):
	url = f'https://ipapi.co/{ip}/json/'
	hc = Http_Client()
	r = hc.get(url)
	r['City'] = r['city']
	r['lat'] = r['latitude']
	r['lon'] = r['longitude']
	return r

def ip_api_com(ip):
	url = f'http://ip-api.com/json/{ip}'
	hc = Http_Client()
	r = hc.get(url)
	r['City'] = r['city']
	return r

def iplocation(ip=None):
	if ip is None:
		ip = get_outip()
	# apikey come from
	# https://app.apiary.io/globaliptv/tests/runs
	# using my github accout
	apikey='c675f89c4a0e9315437a1a5edca9b92c'
	api = f"https://www.iplocate.io/api/lookup/{ip}?apikey={apikey}",
	hc = Http_Client()
	r= hc.get(api, headers=public_headers)
	return r

def get_ip_location(ip):
	funcs = [
		ip_api_com,
		ipapi_co,
		ipip,
		iplocation
	]
	hc = Http_Client()
	for f in funcs:
		try:
			r = f(ip)
			return r
		except:
			pass
		
if __name__ == '__main__':
	print(get_free_local_addr())
	if len(sys.argv) > 1:
		info = get_ip_location(sys.argv[1])
		print(info)

