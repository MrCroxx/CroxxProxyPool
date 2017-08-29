from CroxxProxyPool import ProxyPool
import requests

pp = ProxyPool() # get ProxyPool instance (ProxyPool is a singleton. You can only have ONE instance.)

pp.start(delay = 10 * 60,ssl = True) # start crawling proxies

proxy = pp.pop() # get a proxy

proxies = {
	'http':proxy.toURL(),
	'https':proxy.toURL(),
} # set proxies for requests

headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
} # set headers for requests

res = requests.get('https://www.baidu.com',headers=headers,proxies=proxies) # GET with proxies

print res.ok

pp.push(proxy) # push the proxy back to ProxyPool after using it

# CroxxProxyPool is thread-safe and you can use it in your multithreading spider easily.