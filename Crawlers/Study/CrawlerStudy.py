#!/usr/bin/env python
# coding: utf-8
"""
Created on 2016/11/14
@author: liuzhenrain
"""

import urllib2
import itertools
import re
import urlparse
from robotparser import RobotFileParser
import time
import datetime
import Queue


def download(url, headers, proxy, num_retries, data=None):
    print "download url:", url
    request = urllib2.Request(url, data, headers)
    opener = urllib2.build_opener()
    if proxy:
        proxy_param = {urlparse.urlparse(url).scheme: proxy}
        opener.add_handler(urllib2.ProxyHandler(proxy_param))
    try:
        response = opener.open(request)
        html = response.read()
        code = response.code
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = ''
        if hasattr(e, 'code'):
            code = e.code
            if num_retries > 0 and 500 <= code < 600:
                return download(url, headers, proxy, num_retries - 1, data)
        else:
            code = None
    return html


def get_links(html):
    '''
    Return a list of links from html
    :param html:
    :return:
    '''
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)


def link_crawler(seed_url, link_regex, delay=5, max_depth=-1, max_urls=-1, headers=None, user_agent='wasp', proxy=None,
                 num_retries=1, scrape_callback=None):
    '''
    通过正则表达式来确认最终需要下载的网页
    :param seed_url: 原始根目录
    :param link_regex: 正则表达式（获取超链接）
    :param delay: 每次下载等待时常
    :param max_depth: 最大爬取深度
    :param max_urls:最大爬取数量
    :param headers: html头
    :param user_agent: 爬虫浏览器属性（代理）
    :param proxy: 网络代理
    :param num_retries: 最大重复次数
    :return:
    '''
    # 创建一个双端队列,能够有效的快速插入,但是查找的时候会变慢。双端队列仅维护块索引,所以非常块。
    # 参见: deque.md
    crawler_queue = Queue.deque([seed_url])
    seen = {seed_url: 0}
    # 统计有多少个链接已经被下载
    num_urls = 0
    rp = get_robots(seed_url)
    throttle = Throttle(delay)
    headers = headers or {}
    if user_agent:
        headers['user-agent'] = user_agent
    while crawler_queue:
        url = crawler_queue.pop()
        if rp.can_fetch(user_agent, url):
            throttle.wait(url)
            html = download(url, headers, proxy=proxy, num_retries=num_retries)
            links = []
            if scrape_callback:
                links.extend(scrape_callback(url, html) or [])
            depth = seen[url]
            if depth != max_depth:
                if link_regex:
                    links.extend(link for link in get_links(html) if re.match(link_regex, link))

                for link in links:
                    link = normalize(seed_url, link)
                    if link not in seen:
                        seen[link] = depth + 1
                        if same_domain(seed_url, link):
                            crawler_queue.append(link)
            num_urls += 1
            if num_urls == max_urls:
                break
        else:
            print "Blocked by robots.txt:", url


class Throttle:
    '''
    控制爬虫速度
    '''

    def __init__(self, delay):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        # urlparse.urlparse(url) <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
        # Return a 6-tuple: (scheme, netloc, path, params, query, fragment).
        domain = urlparse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                # domain ha been accessed recently so need to sleep
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.datetime.now()


def normalize(seed_url, link):
    # urldefrag 从链接中的第一个#开始，将链接分割成两部分，第二部分为#之后数据且不带#
    link, _ = urlparse.urldefrag(link)
    return urlparse.urljoin(seed_url, link)


def same_domain(url1, url2):
    '''
    Return True if both URL's belong to same domain
    :param url1:
    :param url2:
    :return: True or False
    '''
    return urlparse.urlparse(url1).netloc == urlparse.urlparse(url2).netloc


def get_robots(url):
    '''
    Initialize robots parser for this domain
    :param url:
    :return:
    '''
    rp = RobotFileParser()
    rp.set_url(urlparse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp


if __name__ == "__main__":
    link_crawler("http://example.webscraping.com/", "/(index|view)/", delay=1, num_retries=2, max_depth=1,
                 user_agent='GoodCrawler')
    pass
