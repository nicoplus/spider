import os

import platform
from splinter import Browser
from selenium import webdriver

import config


def add_chrome_webdriver():
    print(platform.system())
    if platform.system() == 'Windows':
        working_path = os.getcwd()
        library = 'library'
        path = os.path.join(working_path, library)
        os.environ["PATH"] += '{}{}{}'.format(os.pathsep, path, os.pathsep)
        print(os.environ['PATH'])


def add_cookie(cookie):
    # for part in cookie_string.split('; '):
    #     kv = part.split('=')
    #     d = {kv[0]: kv[1]}
    #     print('cookie', d)
    #     cookie.add(d)
    cookie.delete()
    cookie.add({'test':'test'})
    print(cookie.all())


def find_website():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("user-data-dir={}".format(config.profile))
    with Browser('chrome',  options=chrome_options) as browser:
        # Visit URL
        url = "https://www.zhihu.com"
        browser.visit(url)
        browser.execute_script('window.scrollTo(0,document.body.scrollHeight);')
        found = False
        while not found:
            print('loop')
            found = browser.is_text_present('5 天前')
            if found:
                print('拿到了最近5天的个人动态')
                break
            else:
                browser.execute_script('window.scrollTo(0,document.body.scrollHeight);')

def main():
    add_chrome_webdriver()
    find_website()


if __name__ == '__main__':
    main()
