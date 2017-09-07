# -*- coding:utf-8 -*-
import requests, re, heapq, threading, random, time
from lxml import etree
from datetime import datetime, timedelta
from winsound import Beep


class Proxy(object):
    def __init__(self, host, port, protocol):
        self.host = host
        self.port = port
        self.protocol = protocol
        self.timestamp = None
        self.refresh()

    def refresh(self):
        self.timestamp = datetime.now()

    def toURL(self):
        return self.host + ':' + self.port

    def __lt__(self, x):
        return self.timestamp < x.timestamp

    def __str__(self):
        return '<Proxy host = %s port = %s protocol = %s timestamp = %s>' % (
            self.host, self.port, self.protocol, self.timestamp)

    def __repr__(self):
        return str(self)


class Page(object):
    def __init__(self, pid):
        self.pid = pid
        self.timestamp = None
        self.refresh()

    def refresh(self):
        self.timestamp = datetime.now()

    def __lt__(self, x):
        return self.timestamp < x.timestamp

    def __str__(self):
        return '<Page page = %s>' % (self.pid,)

    def __repr__(self):
        return str(self)


class ProxyPool(object):
    def __init__(self, delay=5 * 60, debug=False):
        self.__httpProxyHeap = []
        self.__httpsProxyHeap = []
        self.__proxyset = set()
        self.__pageHeap = []
        self.__mutex = threading.Lock()
        self.__cond = threading.Condition(self.__mutex)
        self.__start = False
        self.__debug = debug
        self.__delay = delay

    def push(self, proxy):
        if self.__start:
            if proxy.toURL() in self.__proxyset:
                if self.__debug:
                    print '[UNPUSH] REPEAT PROXY : ', proxy
                    return False
            else:
                self.__cond.acquire()
                proxy.refresh()
                self.__proxyset.add(proxy.toURL())
                if proxy.protocol == 'HTTP':
                    heapq.heappush(self.__httpProxyHeap, proxy)
                elif proxy.protocol == 'HTTPS':
                    heapq.heappush(self.__httpsProxyHeap, proxy)
                self.__cond.notifyAll()
                self.__cond.release()
                if self.__debug:
                    print '[Size : %s][PUSH] PROXY : ' % (self.size()), proxy
        else:
            print 'ProxyPool has not started yet!'
            return False

    def pop(self, protocol='HTTP'):
        if self.__start:
            self.__cond.acquire()
            proxy = None
            if protocol == 'HTTP':
                while len(self.__httpProxyHeap) == 0:
                    self.__cond.wait()
                proxy = heapq.heappop(self.__httpProxyHeap)
            elif protocol == 'HTTPS':
                while len(self.__httpsProxyHeap) == 0:
                    self.__cond.wait()
                proxy = heapq.heappop(self.__httpsProxyHeap)
            self.__proxyset.remove(proxy.toURL())
            self.__cond.release()
            if self.__debug:
                print '[Size : %s][POP] PROXY : ' % (self.size()), proxy
            return proxy
        else:
            print 'ProxyPool has not started yet!'
            return None

    def size(self):
        if self.__start:
            self.__cond.acquire()
            s = len(self.__httpProxyHeap) + len(self.__httpsProxyHeap)
            self.__cond.release()
            return s
        else:
            print 'ProxyPool has not started yet!'
            return None

    def __crawlProxyList(self, proxy=None):

        proxylist = []

        self.__cond.acquire()

        page = heapq.heappop(self.__pageHeap)
        pid = page.pid
        page.refresh()
        heapq.heappush(self.__pageHeap, page)

        self.__cond.release()

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
        }

        proxies = {}

        if proxy is not None:
            proxies = {
                'http': proxy.toURL(),
                'https': proxy.toURL(),
            }

        # url = 'http://www.xicidaili.com/nn/' + str(pid)
        url = 'http://www.xicidaili.com/wt/' + str(pid)
        try:
            if self.__debug:
                print '[ Crawling Proxy List ... ... ] Proxy : ', proxy

            res = requests.get(url, headers=headers, proxies=proxies)

            html = etree.HTML(res.text)

            ip_list_tables = html.xpath("//table[@id='ip_list']")

            if len(ip_list_tables) == 0:
                if self.__debug:
                    print 'Crawler : Get No IP List ! Proxy : ', proxy
                print 0 / 0

            ip_list_table = html.xpath("//table[@id='ip_list']")[0]

            for tr in ip_list_table.xpath("//tr")[1:]:
                tds = tr.xpath('td')[:]
                proxylist.append(Proxy(tds[1].text, tds[2].text, tds[5].text))

            if self.__debug:
                print '[ Get %s proxies from page %s ! ] Proxy : ' % (len(proxylist), pid), proxy

        except:
            if self.__debug:
                print '[ Bad Crawler ! ] Proxy : ', proxy
        finally:
            for c_proxy in proxylist:
                threading.Thread(target=self.__testProxy, args=(c_proxy,)).start()
            while datetime.now() - self.__pageHeap[0].timestamp < timedelta(minutes=10):
                time.sleep(60)
            threading.Timer(self.__delay, self.__crawlProxyList, (proxy,)).start()
            return proxylist

    def __testProxy(self, proxy):

        url = 'https://www.baidu.com'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
        }

        proxies = {
            'http': proxy.toURL(),
            'https': proxy.toURL(),
        }

        try:
            if self.__debug:
                print '[Testing Proxy...  ...]', proxy
            res = requests.get(url, headers=headers, proxies=proxies)
            if not res.ok:
                print 0 / 0
        except:
            if self.__debug:
                print '[Test]Bad Proxy :', proxy
            return False
        else:
            self.push(proxy)
            if self.__debug:
                print '[Test]Good Proxy :', proxy
            threading.Thread(target=self.__crawlProxyList, args=(proxy,)).start()
            return True

    def start(self):
        if not self.__start:
            self.__start = True
            for pid in range(1, 501):
                heapq.heappush(self.__pageHeap, Page(pid))
            threading.Thread(target=self.__crawlProxyList).start()
            # threading.Thread(target=self.__checkTopProxy('HTTP')).start()
            # threading.Thread(target=self.__checkTopProxy('HTTPS')).start()
        else:
            print 'ProxyPool has already started! Do not start it twice!'

    def __checkTopProxy(self, protocol):
        try:
            if protocol == 'HTTP':
                while datetime.now() - self.__httpProxyHeap[0].timestamp < timedelta(minutes=10):
                    time.sleep(300)
                self.__cond.acquire()
                proxy = heapq.heappop(self.__httpProxyHeap)
                self.__cond.release()
            elif protocol == 'HTTPS':
                while datetime.now() - self.__httpsProxyHeap[0].timestamp < timedelta(minutes=10):
                    time.sleep(300)
                self.__cond.acquire()
                proxy = heapq.heappop(self.__httpsProxyHeap)
                self.__cond.release()
            if self.__debug:
                print '[CHECK] Proxy :',proxy
            threading.Thread(target=self.__testProxy, args=(proxy,)).start()
            threading.Thread(target=self.__checkTopProxy, args=(protocol,)).start()
        except:
            time.sleep(120)
            threading.Thread(target=self.__checkTopProxy, args=(protocol,)).start()
