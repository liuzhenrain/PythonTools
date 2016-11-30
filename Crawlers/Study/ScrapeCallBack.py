#!/usr/bin/env python
# coding: utf-8
"""
Created on 2016/11/30
@author: liuzhenrain
"""
import csv
import re
import lxml.html
import CrawlerStudy


class ScrapeCallBack:
    def __init__(self):
        self.writer = csv.writer(open("countries.csv", "w"))
        # 一下是一个tunple数据 根据浏览器属性查看，肉眼总结出来的 每一行的ID都是:"places_?__row
        self.fields = (
            'area', 'population', 'iso', 'country', 'capital', 'continent', 'tld', 'currency_code', 'currency_name',
            'phone', 'postal_code_format', 'postal_code_regex', 'languages', 'neighbours')
        # 在Init 的时候就写入一行数据
        self.writer.writerow(self.fields)

    def __call__(self, url, html):
        if re.search('/view/', url):  # 匹配链接是否为view界面
            tree = lxml.html.fromstring(html)
            row = []
            for field in self.fields:
                row.append(tree.cssselect('table > tr#places_{}__row > td.w2p_fw'.format(field))[0].text_content())
            self.writer.writerow(row)


if __name__ == '__main__':
    CrawlerStudy.link_crawler("http://example.webscraping.com/", '/(index|view)/', scrape_callback=ScrapeCallBack(),
                              delay=1)
    pass
