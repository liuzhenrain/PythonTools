import os
import sys
import qu_la
import uukanshu

book_array = [
    'UU','BQG'
]

if __name__ == "__main__":
    printStr = []
    for index in range(len(book_array)):
        printStr.append("{0}-{1}".format(index,book_array[index]))
    select = input("先选择网站: "+", ".join(printStr)+" :")
    book_id = input("输入书号：")
    
    if select == '1' :
        print("选中的内容:{0}".format(book_array[int(select)]))