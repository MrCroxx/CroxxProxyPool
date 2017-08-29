#-*- coding:utf-8 -*-

'''

一个爬取链家网北京机场线二手房信息的爬虫

'''

from CroxxProxyPool import ProxyPool,Proxy
import requests
from lxml import etree
import threading
from datetime import datetime
import time
from winsound import Beep

pp = ProxyPool()
pp.start(delay = 120,ssl = True,debug = True)


mutex = threading.Lock()

count = 0

urllist = []

pages = 32



def crawl(page):

	try:		

		global pp,count,mutex,urllist,pages

		print '< Page %s Crawling ... %s of %s >' % (page,count,pages),datetime.now()

		url = 'https://bj.lianjia.com/ditiefang/li653/pg' + str(page)

		headers = {
			'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
		}

		proxy = pp.pop()

		proxies = {
			'http':proxy.toURL(),
			'https':proxy.toURL(),
		}

		print 'Proxy : ',proxy.toURL()

		res = requests.get(url,headers = headers,proxies=proxies)		

		html = etree.HTML(res.text)

		alist = html.xpath("//ul[@class='sellListContent']//div[@class='title']/a")
		if len(alist) == 0:
			print 0/0

		pp.push(proxy)

		mutex.acquire()
		for a in alist:
			urllist.append(a.attrib['href'])

		count += 1
		print '< Page %s Finished ! %s of %s >' % (page,count,pages),datetime.now()
		mutex.release()
	except:
		print '< Page %s Failed ! Restarting ... %s of %s >' % (page,count,pages),datetime.now()
		threading.Thread(target=crawl,args=(page,)).start()

for i in range(1,pages+1):
	threading.Thread(target=crawl,args=(i,)).start()

while count<pages:
	pass

time.sleep(1)
print 'Length : ',len(urllist)


with open('url.txt','a') as f:
	for item in urllist:
		f.write(item+'\n')

Beep(800,1000)