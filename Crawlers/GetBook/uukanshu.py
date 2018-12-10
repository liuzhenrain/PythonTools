#coding:utf-8
import  requests
import threading
from bs4 import BeautifulSoup
import re
import os
import time
import sys
import traceback

req_head={
"Cache-Control": "no-cache,private",
'Content-Encoding': 'gzip',
'Content-Length': '38822',
'Content-Type': 'text/html; charset=gb2312',
'Date': 'Mon, 10 Dec 2018 12:28:44 GMT',
'Server': 'Microsoft-IIS/8.5',
'Set-Cookie': 'fcip=111; expires=Tue, 11-Dec-2018 12:28:44 GMT; path=/',
'Vary': 'Accept-Encoding',
'X-AspNet-Version': '4.0.30319',
'X-Powered-By': 'ASP.NET',
}


req_header={
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

book_array = [
    {
        'url':'http://www.uukanshu.com',
        'name':'悠悠看书'
    },
    {
        'url':'http://www.qu.la/book/',
        'name':'笔趣阁'
    }
]


req_url_base='https://www.uukanshu.com/b/'

class myThread (threading.Thread):   #继承父类threading.Thread
    def __init__(self, threadID, counter,start_page):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.counter = counter
        self.start_page=start_page
    def run(self):                   #把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        #print("编号为1的小说")
        get_txt(self.counter,self.start_page)
        #print("Exiting")


threadLock = threading.Lock()
threads = []


def write_txt_intro(txt,start_page):
    fo = open("txt_intro{0:0>8}_{1:0>8}.txt".format(start_page,start_page+100), "ab+")
    try:
        fo.write(("*#*#{0:0>8}".format(txt['id'])+"\r\n").encode('UTF-8'))
        fo.write(('书籍名称：'+txt['title'] + "\r\n").encode('UTF-8'))
        fo.write(('书籍编号：{0:0>8}\r\n'.format(txt['id'])).encode('UTF-8'))
        fo.write((txt['author'] + "\r\n").encode('UTF-8'))
        fo.write((txt['update'] + "\r\n").encode('UTF-8'))
        fo.write((txt['lately'] + "\r\n").encode('UTF-8'))
        fo.write(("*******简介*******\r\n").encode('UTF-8'))
        fo.write(("\t" + txt['intro'] + "\r\n").encode('UTF-8'))
        fo.write(("******************\r\n").encode('UTF-8'))
        fo.write(("#*#*\r\n").encode('UTF-8'))
    finally:
        fo.close()

#小说下载函数
#id：小说编号
#字段介绍
# tetle：小说题目
# first_page：第一章页面
# txt_section：章节地址
# section_name：章节名称
# section_text：章节正文
# section_ct：章节页数
def get_txt(txt_id,start_page):
    txt={}
    txt['title']=''
    txt['id']=str(txt_id)
    try:
        #print("请输入需要下载的小说编号：")
        #txt['id']=input()
        req_url=req_url_base+ txt['id']+'/'                        #根据小说编号获取小说URL
        #print("小说编号："+txt['id'])
        res=requests.get(req_url,params=req_header)             #获取小说目录界面
        soups=BeautifulSoup(res.text,"html.parser")           #转化
        txt['title']=soups.select('.xiaoshuo_content.clear .jieshao .jieshao_content h1')[0].text         #获取小说题目
        txt['author']=soups.select('.xiaoshuo_content.clear .jieshao .jieshao_content h2 a')[0].text
        # txt['update']=txt['author'][2].text                                                       #获取小说最近更新时间
        # txt['lately'] = txt['author'][3].text                                                     #获取最近更新章节名称
        # txt['author']=txt['author'][0].text                                                       #获取小说作者
        txt['intro']=soups.select('.xiaoshuo_content.clear .jieshao .jieshao_content h3')[0].text.strip()            #获取小说简介
        print("编号："+'{0:0>8}   '.format(txt['id'])+  "小说名：《"+txt['title']+"》  开始下载。")
        #print("正在寻找第一章页面。。。")
        first_page=soups.select('.xiaoshuo_content.clear .zhangjie #chapterList li a')                          #获取小说所有章节信息
        section_ct=len(first_page)                                                                  #获取小说总章页面数
        first_page = str(start_page) +".html"  #first_page[0]['href']                                        #获取小说第一章页面地址
        print("小说章节页数："+str(section_ct))
        print("第一章地址寻找成功："+ first_page)
        txt_section=first_page                                                                  #设置现在下载小说章节页面
        # write_txt_intro(txt,start_page)
        fo = open('{0:0>8}-{1}.txt.download'.format(txt['id'],txt['title']), "ab+")         #打开小说文件
        fo.write((txt['title']+"\r\n").encode('UTF-8'))
        fo.write((txt['author'] + "\r\n").encode('UTF-8'))
        # fo.write((txt['update'] + "\r\n").encode('UTF-8'))
        # fo.write((txt['lately'] + "\r\n").encode('UTF-8'))
        fo.write(("*******简介*******\r\n").encode('UTF-8'))
        fo.write(("\t"+txt['intro'] + "\r\n").encode('UTF-8'))
        fo.write(("******************\r\n").encode('UTF-8'))
        while(1):
            try:
                r=requests.get(req_url+str(txt_section),params=req_header)                      #请求当前章节页面
                content = re.sub("&#",'',r.text)
                soup=BeautifulSoup(content,"html.parser")                                        #soup转换
                section_name=soup.select('.h1title #timu')[0].text                             #获取章节名称
                section_text=soup.select('#contentbox')[0]
                for ss in section_text.select("script"):
                    ss.decompose()
                section_text=re.sub('\s+', '\r\n\t', section_text.text).strip('\r\n')#获取章节文本
                next_a=soup.select_one('#next')                      #获取下一章地址
                if(next_a.next == '全文完'):
                    print("编号："+'{0:0>8}   '.format(txt['id'])+  "小说名：《"+txt['title']+"》 下载完成")
                    break
                else:
                    txt_section = next_a['href'].split('/')[3]
                fo.write(('\r'+section_name+'\r\n').encode('UTF-8'))                                #以二进制写入章节题目
                fo.write((section_text).encode('UTF-8'))                        #以二进制写入章节内容
                print(txt['title']+' 章节：'+section_name+'     已下载')
                #print(section_text.text.encode('UTF-8'))
            except:
                print(traceback.print_exc())
                print("编号："+'{0:0>8}   '.format(txt['id'])+  "章节：《"+section_name+"》 章节下载失败，正在重新下载。")
        fo.close()
        os.rename('{0:0>8}-{1}.txt.download'.format(txt['id'],txt['title']), '{0:0>8}-{1}.txt'.format(txt['id'],txt['title']))
    except:
        fo_err = open('dowload.log', "ab+")
        try:
            fo_err.write(('['+time.strftime('%Y-%m-%d %X', time.localtime())+"]：编号：" + '{0:0>8}   '.format(txt['id']) + "小说名：《" + txt['title'] + "》 下载失败。\r\n").encode('UTF-8'))
            print('['+time.strftime('%Y-%m-%d %X', time.localtime())+"]：编号："+'{0:0>8}   '.format(txt['id'])+  "小说名：《"+txt['title']+"》 下载失败。")
            os.rename('{0:0>8}'.format(txt['id']) + '-' + txt['title'] + '.txt.download',
                  '{0:0>8}'.format(txt['id']) + '-' + txt['title'] + '.txt.error')
        except:
            fo_err.write(('['+time.strftime('%Y-%m-%d %X', time.localtime())+"]：编号："+'{0:0>8}   '.format(txt['id'])+"下载失败。\r\n").encode('UTF-8'))
            print('['+time.strftime('%Y-%m-%d %X', time.localtime())+"]：编号："+'{0:0>8}   '.format(txt['id'])+"下载失败。")
        finally:
            fo_err.close()

#批量获取txt  900-1000
def get_txts(start_page):
    print("当前起始页面："+str(start_page))
    print("正在创建下载任务。")
    for i in range(start_page, start_page+100):
        thread_one = myThread(i, str(i),start_page)
        thread_one.start()
        threads.append(thread_one)
    print("下载任务创建完成。")
    print("等待下载任务完成。。。")
    task_ct = len(threads)
    print('********************')
    i_ls_ct = 0
    while (1):
        run_task = 0
        for i in threads:
            if (i.isAlive()):
                run_task += 1
        # os.system('cls')
        # write('\b'+"总任务数：" + str(task_ct) + "  已完成任务数：" + str(task_ct - run_task)+"\r")
        if (i_ls_ct % 10 >= 4):
            print('{0:0>8}-{1:0>8} '.format(start_page,start_page+100)+"下载中："
                  + "*" * (int)((task_ct - run_task) / task_ct * 50) + "_" * (int)(
                run_task / task_ct * 50) + " /. 总数：" + str(task_ct) + "  已完成：" + str(task_ct - run_task), end="\r")
        else:
            print('{0:0>8}-{1:0>8} '.format(start_page,start_page+100)+"下载中："
                  + "*" * (int)((task_ct - run_task) / task_ct * 50) + "_" * (int)(
                run_task / task_ct * 50) + " \. 总数：" + str(task_ct) + "  已完成：" + str(
                task_ct - run_task), end="\r")
        if (run_task == 0):
            break
        time.sleep(.1)
        if (i_ls_ct > 100000):
            i_ls_ct = 0
        else:
            i_ls_ct += 1
            # print(i_ls_ct)
    print("所有下载任务已完成")
    time.sleep(2)
    os.system('cls' if os.name == 'nt' else "printf '\033c'")

#get_txt(764066)
# if __name__=='__main__':
#     pass
    # print("请输入需要下载的小说编号：")
    # txt_id = input()
    # get_txt(txt_id,3808382)

    # 创建新线程
    # for i_ls in range(9,50):
    #     get_txts(i_ls*100)

#cd get_txt
#python get_txt.py