# CroxxProxyPool



CroxxProxyPool is a light, thread-safe ProxyPool for Python that automatically crawl free proxies.



## Advantages

1. Thread-safe.
2. Use a heap to make sure each time you will pop the earliest proxy you used.
3. Confirm the availability of a proxy when it is crawled.
4. Detect repeat proxies when pushing.
5. [ Update on 2017-8-30 ] Crawl other proxies with a searched proxy to fasten searching available proxies ! ( Searching can be 2-5 times faster than before ! )



## Usage

1.Import CroxxProxyPool

```python
from CroxxProxyPool import ProxyPool
```

2.Get instance

```python
pp = ProxyPool()
# get ProxyPool instance (ProxyPool is a singleton. You can only have ONE instance.)
```

3.Start crawling proxies

```python
pp.start(delay = 10 * 60,ssl = True)
# start crawling proxies
```

4.Get a proxy by pop()

```python
proxy = pp.pop()
# get a proxy
```

5.Push the proxy back after using it

```python
pp.push(proxy)
# push the proxy back to ProxyPool after using it
```

### thread-safe

CroxxProxyPool is a thread-safe ProxyPool.

This is a multithreading emample.

(The log of function 'TsetProxy' is not thread-safe, for print in python2.7 is not thread-safe.)

```python
from CroxxProxyPool import ProxyPool
import threading,time,random

pp = ProxyPool()
pp.start(delay = 10 * 60,ssl = True,debug = True)


def testThread(tid,pp):
	s1 = random.randint(0,40)
	time.sleep(s1)
	proxy = pp.pop(debug=True)
	s2 = random.randint(0,5)
	time.sleep(s2)
	pp.push(proxy,debug=True)

for i in range(0,300):
	threading.Thread(target = testThread,args = (i,pp)).start()
```

