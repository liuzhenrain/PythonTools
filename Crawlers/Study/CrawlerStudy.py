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
from robotparser import RobotFileParser as rp
import time
import datetime
import Queue


def download(url, user_agent="wswp", numretries=2):
    print "download url:", url
    headers = {'User-agent': user_agent}
    request = urllib2.Request(url, headers=headers)
    try:
        html = urllib2.urlopen(request).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        if numretries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return download(url, numretries - 1)
        html = None
    return html


def looppage():
    for page in itertools.count(1):
        loadurl = 'http://example.webscraping.com/view/-%d' % page
        html = download(loadurl)
        if html is None:
            break
        else:
            pass


def get_links(html):
    '''
    Return a list of links from html
    :param html:
    :return:
    '''
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)


def link_crawler(seed_url, link_regex, max_depth=2):
    '''
    通过正则表达式来确认最终需要下载的网页
    :param seed_url:
    :param link_regex:
    :return:
    '''
    # 创建一个双端队列,能够有效的快速插入,但是查找的时候会变慢。双端队列仅维护块索引,所以非常块。
    # 参见: deque.md
    crawler_queue = Queue.deque([seed_url])
    seen = {}
    seen = set(crawler_queue)
    throttle = Throttle(2)
    while crawler_queue:
        url = crawler_queue.pop()
        throttle.wait(url)
        html = download(url)
        for link in get_links(html):
            print link
            if re.match(link_regex, link):
                link = urlparse.urljoin(seed_url, link)
                if link not in seen:
                    seen.add(link)
                    crawler_queue.append(link)


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


if __name__ == "__main__":
    link_crawler("http://example.webscraping.com", "/(index|view)/")
    pass
