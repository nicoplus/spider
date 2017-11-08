from gevent.pool import Pool

from requests.exceptions import RequestException

from utils import fetch
from models import Proxy

pool = Pool(10)

def check_proxy(p):
	print 'checking proxy %s'%p['address']
	try:
		fetch('http://www.baidu.com', proxy=p['address'])
	except RequestException:
		p.delete()

pool.map(check_proxy, Proxy.objects.all())
print Proxy.objects.count()