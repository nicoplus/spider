from datetime import datetime

from requests.exceptions import Timeout, ConnectionError
from gevent import monkey, sleep, GreenletExit
from gevent.queue import Queue, Empty
from gevent.pool import Pool
monkey.patch_all()

from pymongo.errors import InvalidBSON
from mongoengine import NotUniqueError, DoesNotExist
from bs4 import BeautifulSoup

from utils import fetch
from models import Proxy, Article, Publisher

SEARCH_URL = 'http://weixin.sogou.com/weixin?query={}&type=2&page={}'
SEARCH_KEY_WORDS = 'python'


def save_search_result(page, queue, retry=0):
    proxy = Proxy.get_random()['address']
    url = SEARCH_URL.format(SEARCH_KEY_WORDS, page)
    try:
        r = fetch(url, proxy)
    except (Timeout, ConnectionError):
        sleep(0.5)
        retry += 1
        if retry > 6:
            queue.put(page)
            raise GreenletExit()
        try:
            p = Proxy.objects.get(address=proxy)
            if p:
                p.delete()
        except DoesNotExist:
            pass

        return save_search_result(page, queue, retry)
    soup = BeautifulSoup(r.text, 'lxml')
    results = soup.find(class_='news-box')
    if results is None:
        sleep(0.5)
        retry += 1
        if retry > 6:
            queue.put(page)
            print 'greenlei exit'
            raise GreenletExit()
        return save_search_result(page, queue, retry)
    articles = results.find('ul', class_='news-list').find_all('li')
    print 'url:%s--articles:%s' % (url, len(articles))

    for article in articles:
        save_article(article)


def save_article(article_):
    txt_box = None
    img_box = article_.find(class_='img-box')
    if img_box is not None:
        img_url = img_box.find('a').find('img').attrs['src'].split('url=')[1]
    else:
        txt_box = article_.find(class_='txt-box')
        img_url = txt_box.find(
            class_='img-d').a.span.img.attrs['src'].split('url=')[1]

    if txt_box is None:
        txt_box = article_.find(class_='txt-box')
    title = txt_box.find('h3').find('a').text
    article_url = txt_box.find('h3').find('a').attrs['href']
    summary = txt_box.find('p').text
    create_at = datetime.fromtimestamp(
        float(txt_box.find(class_='s-p').attrs['t']))
    publish_name = txt_box.find(class_='s-p').find('a').get_text()

    article = Article(img_url=img_url, title=title, url=article_url, summary=summary,
                      create_at=create_at, publisher=Publisher.get_or_create(publish_name))

    try:
        article.save()
    except (NotUniqueError, InvalidBSON):
        pass


def save_search_result_with_queue(queue):
    while 1:
        try:
            p = queue.get(timeout=0)
        except Empty:
            break
        save_search_result(p, queue)
    print 'stopping crawler...'


def use_gevent_with_queue():
    queue = Queue()
    pool = Pool(5)

    for p in range(1, 7):
        queue.put(p)

    while pool.free_count():
        sleep(0.1)
        pool.spawn(save_search_result_with_queue, queue)

    pool.join()


if __name__ == '__main__':
    use_gevent_with_queue()
