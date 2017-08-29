
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