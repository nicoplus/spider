import os
import requests
import config


class Model():
    """
    基类, 用来显示类的信息
    """

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


def get(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/61.0.3163.100 '
                      'Safari/537.36',
        'Cookie': config.cookie,
    }
    r = requests.get(url, headers=headers)
    return r.content


def main():
    url = 'https://www.zhihu.com/'
    page = get(url)
    print(page.decode())


if __name__ == '__main__':
    main()
