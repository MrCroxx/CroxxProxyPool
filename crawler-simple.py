#-*- coding:utf-8 -*-

'''

一个爬取链家网北京2号线二手房信息的爬虫

'''

from CroxxProxyPool import ProxyPool,Proxy
import requests
from lxml import etree
import threading
from datetime import datetime
import time
from winsound import Beep

pp = ProxyPool()
pp.start(source = 'xicidaili',delay = 30,ssl = True,debug = False)


mutex = threading.Lock()

count = 0

pages = 49



def crawl(page):

	try:		

		global pp,count,mutex,pages		

		url = 'https://bj.lianjia.com/ditiefang/li656/pg' + str(page)

		headers = {
			'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
		}

		proxy = pp.pop()

		print '< Page %s Crawling ... %s of %s >' % (page,count,pages),datetime.now()

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

		with open('url.txt','a') as f:
			for a in alist:
				f.write(a.attrib['href'] + '\n')

		count += 1
		print '< Page %s Finished ! %s of %s >' % (page,count,pages),datetime.now()
		Beep(800,300)
		mutex.release()
	except:
		print '< Page %s Failed ! Restarting ... %s of %s >' % (page,count,pages),datetime.now()
		threading.Thread(target=crawl,args=(page,)).start()

for i in range(1,pages+1):
	threading.Thread(target=crawl,args=(i,)).start()

while count < pages:
	pass

time.sleep(1)

Beep(800,2000)

pp.stop()