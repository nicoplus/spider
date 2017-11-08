# coding=utf-8
import re
import threading
from multiprocessing.dummy import Pool as ThreadPool

import requests
from mongoengine import NotUniqueError

from models import Proxy
from config import PROXY_SITES, PROXY_REGX, PROXY_REGEX
from utils import fetch


def save_proxies(url):
    try:
        r = fetch(url)
    except requests.exceptions.RequestException:
        print('false...:%s' % (url,))
        return False
    print('success......:%s' % url)
    addresses = re.findall(PROXY_REGEX, r.text)  # PROXY_REGX OR PROXY_REGEX
    print("%s----%s" % (url, len(addresses)))
    for address in addresses:
        proxy = Proxy(address=address)
        try:
            proxy.save()
        except NotUniqueError:
            pass


def update_proxy_sites(prxoy_sites=None):
    if prxoy_sites is None:
        return []
    proxy_sites_update = []
    for url in prxoy_sites:
        if 'http://www.youdaili.net/Daili/http/' in url:

            for i in xrange(2, 6):
                list_url = url.split('.')
                list_url[2] += '_' + str(i)
                str_url = '.'.join(list_url)
                proxy_sites_update.append(str_url)
        proxy_sites_update.append(url)
    return proxy_sites_update


def cleanup():
    Proxy.drop_collection()


def non_thread():
    cleanup()
    for url in update_proxy_sites(PROXY_SITES):
        save_proxies(url)


def use_thread():
    cleanup()
    threads = []
    for url in update_proxy_sites(PROXY_SITES):
        t = threading.Thread(target=save_proxies, args=(url,))
        t.setDaemon(True)
        threads.append(t)
        t.start()

    for th in threads:
        th.join()


def use_thread_pool():
    cleanup()
    pool = ThreadPool(5)
    urls = update_proxy_sites(PROXY_SITES)
    pool.map(save_proxies, urls)
    pool.close()
    pool.join()


if __name__ == '__main__':

    use_thread_pool()
