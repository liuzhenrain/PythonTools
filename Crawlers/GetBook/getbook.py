import os
import sys
import qu_la
import uukanshu

book_array = [
    '悠悠看书 www.uukanshu.com','笔趣阁 www.bq.la'
]

if __name__ == "__main__":
    printStr = []
    for index in range(len(book_array)):
        printStr.append("{0}-{1}".format(index,book_array[index]))
    select = input("先选择网站: "+", ".join(printStr)+" :")
    book_id = input("输入书号：")
    start_page = input("输入起始页号")
    if select == '0' :
        uukanshu.get_txt(book_id,start_page)