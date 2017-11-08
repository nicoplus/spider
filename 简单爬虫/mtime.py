import os
import requests
from pyquery import PyQuery as pq


class Model:
    """
    基类, 用来显示类的信息
    """
    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class MtimeMovieModel(Model):
    def __init__(self):
        self.name = ''
        self.score = 0
        self.quote = ''
        self.cover_url = ''
        self.ranking = 0


def movie_from_div(div):
    """
    从一个 div 里面获取到一个电影信息
    """
    e = pq(div)

    # 小作用域变量用单字符
    m = MtimeMovieModel()
    m.name = e('.mov_con').find('h2').find('a').text()
    m.score = e('.total').text() + e('.total2').text()
    m.quote = e('.mt3').text()
    m.cover_url = e('img').attr('src')
    m.ranking = e('.number').find('em').text()

    return m


def movies_from_url(url):
    """
    从 url 中下载网页并解析出页面内所有的电影
    """
    r = requests.get(url)
    page = r.content
    e = pq(page)
    items = e('#asyncRatingRegion').find('li')
    # 调用 movie_from_div
    print('items---', items)
    movies = [movie_from_div(i) for i in items]
    return movies


def main():
    # 在页面上点击下一页, 观察 url 变化, 找到规律

    movies = movies_from_url('http://www.mtime.com/top/movie/top100/')
    print('top250 movies', movies)

    for i in range(2, 11):
        url = 'http://www.mtime.com/top/movie/top100/index-{}.html'.format(i)
        movies = movies_from_url(url)
        print('top250 movies', movies)


if __name__ == '__main__':
    main()
