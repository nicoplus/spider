import Queue
import re
import threading

import requests
from mongoengine import NotUniqueError

from models import Proxy
from config import PROXY_REGEX, PROXY_SITES
from utils import fetch


def save_proxies(url):
    proxies = []
    try:
        r = fetch(url)
    except requests.exceptions.RequestException:
        return False
    addresses = re.findall(PROXY_REGEX, r.text)
    for address in addresses:
        proxy = Proxy(address=address)
        try:
            proxy.save()
        except NotUniqueError:
            pass
        else:
            proxies.append(address)
    return proxies


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


def save_proxies_with_queue(queue):
    while 1:
        url = queue.get()
        save_proxies(url)
        queue.task_done()


def use_thread_with_queue():
    cleanup()
    queue = Queue.Queue()

    for i in range(5):
        th = threading.Thread(target=save_proxies_with_queue, args=(queue,))
        th.setDaemon(True)
        th.start()

    for url in update_proxy_sites(PROXY_SITES):
        queue.put(url)

    queue.join()


def save_proxies_with_queue2(in_queue, out_queue):
    while True:
        url = in_queue.get()
        rs = save_proxies(url)
        out_queue.put(rs)
        in_queue.task_done()


def append_result(out_queue, result):
    while True:
        rs = out_queue.get()
        if rs:
            result.extend(rs)
        out_queue.task_done()


def use_thread_with_queue2():
    cleanup()
    in_queue = Queue.Queue()
    out_queue = Queue.Queue()

    for i in range(5):
        th = threading.Thread(
            target=save_proxies_with_queue2, args=(in_queue, out_queue))
        th.setDaemon(True)
        th.start()

    for url in update_proxy_sites(PROXY_SITES):
        in_queue.put(url)

    result = []

    for i in range(5):
        th = threading.Thread(target=append_result, args=(out_queue, result))
        th.setDaemon(True)
        th.start()

    in_queue.join()
    out_queue.join()

    print len(result)


if __name__ == '__main__':
    use_thread_with_queue2()
