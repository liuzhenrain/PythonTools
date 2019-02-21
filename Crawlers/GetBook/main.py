import os,random
import getProxy
import uukanshu_parse
import requests

req_header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': 'fcip=111; ASP.NET_SessionId=wufktsfuinko3v1k5l15iqto; lastread=5366%3D30159%3D%u4E00%20%u751F%u6B7B%u52FF%u8BBA',
    'DNT': '1',
    'Host': 'www.uukanshu.com',
    'Referer': 'https://www.google.com/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
}

UUKANSHU_SITE = "https://www.uukanshu.com/"
UU_TYPE = "1"
PROXIES = list()


def __get_menu_url(novel_site, menu_page_no):
    menu_url = ""
    if novel_site == UU_TYPE:
        menu_url = UUKANSHU_SITE+'/b/'+menu_page_no
    return menu_url

def _get_menu_parse_func(novel_site):
    if novel_site == UU_TYPE:
        return uukanshu_parse.parse_menu

def _parse_menu(novel_site, menu_url):
    menu_page = requests.get(menu_url,headers = req_header)
    menu_parse_func = _get_menu_parse_func(novel_site)
    return menu_parse_func(menu_page)
    


def get_text(novel_site: str, menu_page: str):
    fp = open('proxies.txt', 'r')
    ips = fp.readlines()
    for p in ips:
        proxy = {"proxy": p}
        PROXIES.append(proxy)
    menu_url = __get_menu_url(novel_site,menu_page)
    chapter_dic = _parse_menu(novel_site, menu_url)


if __name__ == "__main__":
    update_proxies = input("是否更新代理数据(y/n):")
    novel_site = input("小说网站，1.UU 看书 -> ")
    novel_menu_no = input("小说目录页编号 -> ")
    if update_proxies == 'y':
        getProxy.start_get_proxy()
    else:
        if not os.path.isfile('proxies.txt'):
            getProxy.start_get_proxy()
    get_text(novel_site, novel_menu_no)
