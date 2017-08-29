#-*- coding:utf-8 -*-

'''

一个爬取链家网北京机场线二手房信息的爬虫

'''

from CroxxProxyPool import ProxyPool,Proxy
import requests
from lxml import etree
import threading

pp = ProxyPool()
pp.start(ssl = True)


mutex = threading.Lock()

count = 0

urllist = []



def crawl(page):

	try:		

		global pp,count,mutex,urllist

		print '< Page %s Crawling ... %s of %s >' % (page,count,11)

		url = 'https://bj.lianjia.com/ditiefang/li654/pg' + str(page)

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

		pp.push(proxy)

		html = etree.HTML(res.text)

		alist = html.xpath("//ul[@class='sellListContent']//div[@class='title']/a")
		if len(alist) == 0:
			print 0/0
		mutex.acquire()
		for a in alist:
			urllist.append(a.attrib['href'])

		count += 1
		print '< Page %s Finished ! %s of %s >' % (page,count,11)
		mutex.release()
	except:
		print '< Page %s Failed ! Restarting ... %s of %s >' % (page,count,11)
		threading.Thread(target=crawl,args=(page,)).start()

for i in range(1,12):
	threading.Thread(target=crawl,args=(i,)).start()

while count<11:
	pass

print 'Length : ',len(urllist)
print urllist


with open('url.txt','a') as f:
	for item in urllist:
		f.write(item+'\n')