#-*- coding:utf-8 -*-
import requests
import re
from lxml import etree
from datetime import datetime
import heapq
import threading
import time,random

class Proxy(object):
	def __init__(self,host,port):
		self.host = host
		self.port = port
		self.refresh()
	def getPriority(self):
		return self.timestamp
	def refresh(self):
		self.timestamp = datetime.now()
	def __lt__(self,x):
		return self.timestamp < x.timestamp
	def __str__(self):
		return '<Proxy host = %s port = %s timestamp = %s>' % (self.host,self.port,self.timestamp)
	def __repr__(self):
		return str(self)

class ProxyHeap(object):
	def __init__(self,source,debug):
		self.__heap = self.__getProxyHeap(source,debug)
		self.__save = self.__heap[:]

	def push(self,item):
		if item in self.__save:
			item.refresh()
			heapq.heappush(self.__heap,item)
			return True
		else:
			return False

	def pop(self):
		return heapq.heappop(self.__heap)

	def empty(self):
		if len(self.__heap) == 0:
			return True
		else:
			return False

	def __getProxyHeap(self,source,debug):

		proxyheap = []

		headers = {
			'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
		}

		if source=='xicidaili':

			res = requests.get("http://www.xicidaili.com/wt",headers=headers)
			html = etree.HTML(res.text)

			ip_list_tables = html.xpath("//table[@id='ip_list']")

			if len(ip_list_tables)==0:
				print 'Crawler : Get No IP List !'
				return []

			ip_list_table = html.xpath("//table[@id='ip_list']")[0]

			for tr in ip_list_table.xpath("//tr")[1:]:
				tds = tr.xpath('td')[1:3]
				#proxylist.append(Proxy(tds[0].text,tds[1].text))
				heapq.heappush(proxyheap,Proxy(tds[0].text,tds[1].text))

			if debug:
				print 'Get Proxy List ( %s items) :' % ( len(proxyheap) ,)
				for item in proxyheap:
					print item

		return proxyheap

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
	def start(self,delay = 10 * 60,source = 'xicidaili',debug = False):
		if self.__start:
			'ProxyPool has already started. Do not start it again!'
		else:
			#self.__timer = threading.Timer(delay,self.refresh,(source,debug))
			self.refresh(delay,source,debug)

	def stop(self):
		if not self.__start:
			'ProxyPool has already stoped. Do not stop it again!'		

	def pop(self,debug = False):
		self.__cond.acquire()
		while self.__proxyheap is None:
			self.__cond.wait()
		while self.__proxyheap.empty():
			self.__cond.wait()
		item = self.__proxyheap.pop()
		if debug:
			print 'POP : ',item
		self.__cond.notify()
		self.__cond.release()
		return item

	def push(self,item,debug = False):
		self.__cond.acquire()
		flag = self.__proxyheap.push(item)
		if debug:
			if flag:
				print 'PUSH : ',item
			else:
				print 'PUSH(OVERDUE) : ',item
		self.__cond.notify()
		self.__cond.release()

	def refresh(self,delay,source,debug):
		self.__cond.acquire()
		self.__proxyheap = ProxyHeap(source,debug)		
		self.__cond.notifyAll()
		self.__cond.release()
		self.__timer = threading.Timer(delay,self.refresh,(delay,source,debug))
		self.__timer.start()

# TODO : add function to test the network condition of the proxies
# TODO : add a README
# TODO : add doc