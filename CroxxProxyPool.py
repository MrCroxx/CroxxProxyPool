#-*- coding:utf-8 -*-
import requests
import re
from lxml import etree
from datetime import datetime
import heapq
import threading
import random

def getProxyList(source,ssl,debug):

	proxylist = []

	headers = {
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
	}

	if source=='xicidaili':

		if ssl:
			res = requests.get("http://www.xicidaili.com/wn/"+str(random.randint(1,11)),headers=headers)
		else:
			res = requests.get("http://www.xicidaili.com/wt",headers=headers)
		html = etree.HTML(res.text)

		ip_list_tables = html.xpath("//table[@id='ip_list']")

		if len(ip_list_tables)==0:
			print 'Crawler : Get No IP List !'
			return []

		ip_list_table = html.xpath("//table[@id='ip_list']")[0]

		for tr in ip_list_table.xpath("//tr")[1:]:
			tds = tr.xpath('td')[1:3]
			proxylist.append(Proxy(tds[0].text,tds[1].text))
			

		if debug:
			print 'Get Proxy List ( %s items) :' % ( len(proxylist) ,)
			for item in proxylist:
				print item

	return proxylist

def TestProxy(proxy,ssl = False,url = None,debug = False,pp = None):
	if url is None:
		if ssl:
			url = 'https://www.baidu.com'
		else:
			url = 'http://www.hao123.com'
	headers = {
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
	}
	proxies = {
		'http':proxy.toURL(),
		'https':proxy.toURL(),
	}
	if debug:
		print 'Testing Proxy',proxy,'ssl = %s url = %s' % (ssl,url)
	try:
		res = requests.get(url,headers=headers,proxies=proxies)
	except:
		if debug:
			print '[BAD]',proxy
		return False
	else:
		if debug:
			print '[GOOD]',proxy
		if pp is not None:
			pp.push(proxy,debug=debug)
		return True

class Proxy(object):
	def __init__(self,host,port):
		self.host = host
		self.port = port
		self.refresh()
	def getPriority(self):
		return self.timestamp
	def refresh(self):
		self.timestamp = datetime.now()
	def toURL(self):
		return self.host+':'+self.port
	def __lt__(self,x):
		return self.timestamp < x.timestamp
	def __str__(self):
		return '<Proxy host = %s port = %s timestamp = %s>' % (self.host,self.port,self.timestamp)
	def __repr__(self):
		return str(self)

class ProxyHeap(object):
	def __init__(self):
		self.__heap = []

	def push(self,item):
		item.refresh()
		heapq.heappush(self.__heap,item)

	def pop(self):
		return heapq.heappop(self.__heap)

	def empty(self):
		if len(self.__heap) == 0:
			return True
		else:
			return False

	def length(self):
		return len(self.__heap)

	def __str__(self):
		s = '<ProxyHeap ( %s items in all )' % len((self.__heap))
		for item in self.__heap:
			s += '\n' + str(item)
		return s


class ProxyPool(object):
	__instance = None	
	def __init__(self):
		pass
	def __new__(cls,*args,**kwargs):
		if ProxyPool.__instance is None:
			ProxyPool.__instance = super(ProxyPool,cls).__new__(cls,*args,**kwargs)
			ProxyPool.__instance.__start = False
			ProxyPool.__instance.__proxyheap = None
			ProxyPool.__instance.__mutex = threading.Lock()
			ProxyPool.__instance.__cond = threading.Condition(ProxyPool.__instance.__mutex)
		return ProxyPool.__instance
	def __str__(self):
		return '<ProxyPool object(singleton)>'
	def __repr__(self):
		return str(self)
	def start(self,delay = 10 * 60,source = 'xicidaili',ssl = False,debug = False):
		if self.__start:
			'ProxyPool has already started. Do not start it again!'
		else:
			self.__start = True
			self.__proxyset = set()
			self.__proxyheap = ProxyHeap()	
			#self.__timer = threading.Timer(delay,self.refresh,(source,debug))
			self.refresh(delay,source,ssl,debug)

	def stop(self):
		if not self.__start:
			'ProxyPool has already stoped. Do not stop it again!'		

	def pop(self,debug = False):
		if self.__start:
			self.__cond.acquire()
			while self.__proxyheap is None:
				self.__cond.wait()
			while self.__proxyheap.empty():
				self.__cond.wait()
			item = self.__proxyheap.pop()
			self.__proxyset.remove(item.toURL())
			if debug:
				print 'POP : ',item,'[ %s LEFT ]' % (self.__proxyheap.length(),)
			self.__cond.notify()
			self.__cond.release()
			return item
		else:
			print 'Please start ProxyPool first !'
			return None

	def push(self,item,debug = False):
		if self.__start:
			self.__cond.acquire()
			if item.toURL() not in self.__proxyset:
				self.__proxyset.add(item.toURL())
				flag = self.__proxyheap.push(item)
				if debug:
					print 'PUSH : ',item,'[ %s LEFT ]' % (self.__proxyheap.length(),)
			else:
				if debug:
					print 'UNPUSH[REPEAT] : ',item,'[ %s LEFT ]' % (self.__proxyheap.length(),)
			self.__cond.notify()
			self.__cond.release()

	def refresh(self,delay,source,ssl,debug):
		proxylist = getProxyList(source,ssl,debug)
		for p in proxylist:
			threading.Thread(target = TestProxy,kwargs = {'proxy':p,'ssl':ssl,'debug':debug,'pp':self}).start()
		self.__timer = threading.Timer(delay,self.refresh,(delay,source,ssl,debug))
		self.__timer.start()

	def length(self):
		return self.__proxyheap.length()

# TODO : add a README
# TODO : add doc