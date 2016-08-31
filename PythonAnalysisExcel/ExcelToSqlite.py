#!/usr/bin/env python
# coding: utf-8
"""
Created on 2016/7/26
@author: liuzhenrain
"""

import glob
import threading

import DataAccess
from ccfile import *
from ccsf import *

# Excel存储目录
pathFolder = ""


# 获取制定文件夹内所有的制定类型的文件
# path：文件夹路径
# wilcard:文件后缀名
# recursion: 是否遍历子目录
def getFileList(path, wildcard, recursion):
    # 改变工作路径到指定的路径
    # os.chdir(path)

    fileList = []

    # 查找文件夹下所有的文件
    files = os.listdir(path)

    # 遍历所有的文件
    for name in files:
        # 获取完整的路径名，用于判定是否为文件夹
        fullname = os.path.join(path, name)
        if (os.path.isdir(fullname) & recursion):
            getFileList(fullname, wildcard, recursion)
        else:
            if (name.endswith(wildcard)):
                fileList.append(name)
    # print fileList.__len__()
    # 可以返回多个值，超多数据
    return fileList


def main(folderPath, modifyList=[]):
    has_db = False
    if not os.path.exists("steelray.db"):
        has_db = False
    else:
        has_db = True

    fileList = []
    if len(modifyList)<=0 and has_db:
        return
    if len(modifyList) <= 0 or (not has_db):
        fileList = glob.glob1(folderPath, "*.xls")
    else:
        for fileinfo in modifyList:
            fileList.append(os.path.split(fileinfo["name"])[1])

    # for item in fileList:
    #     print "excel to sqlite:", item, "filename:", str(item).replace(folderPath + "\\", "")
    # exit()

    # globfiles = glob.glob(folderPath)
    sql_command_array = []
    # for item in globfiles:
    #     print item,os.path.getmtime(item)



    # ticks = time.time()
    # localtime = time.localtime(ticks)
    # timestr = "-".join([str(localtime.tm_year), str(localtime.tm_mon), str(localtime.tm_mday)])
    # print timestr
    sql_count = 0

    # if os.path.exists("commandFiles"):
    #     print "已经有了command文件了"
    # else:
    #     print "还没有command文件"
    #     os.mkdir("commandFiles")
    #
    # if not os.path.exists("commandFiles/commandFile(%s).txt" % timestr) and has_db:
    #     file_list = open("commandFiles/filelist.txt", "a")
    #     file_list.write("commandFile(%s).zip\n" % timestr)
    #     file_list.close()
    threads = []
    t1 = threading.Thread(target=create_macro_file, args=(folderPath,))
    threads.append(t1)
    t1.start()
    # create_macro_file(folderPath)

    for item in fileList:
        # if not item.__contains__("achieve"):
        #     continue
        excel_data_dic = readexcel(item)
        t2 = threading.Thread(target=create_csfile, args=(folderPath + os.sep + "Structs", excel_data_dic,))
        threads.append(t2)
        t2.start()
        sql_command_array = DataAccess.SaveToSqlite("steelray.db", excel_data_dic, has_db)
        # create_csfile(folderPath + os.sep + "csfiles", excel_data_dic)
        # 防止第一次导入数据库时生成超大SQL文件
        if has_db and len(sql_command_array) > 0:
            create_command_file(has_db, sql_command_array)
        sql_count += len(sql_command_array)
        sql_command_array = []
    print "查询语句总条数:", sql_count
    LogCtrl.write_log_file()
    for item in threads:
        item.join()

'''
if __name__ == "__main__":
    # 指定excel文件的位置
    # os.path.abspath('.') 会找到当前py文件的文件夹路径
    # os.sep 确定当前系统的路径分隔符，可以使用 print os.sep 打印看一下
    pathFolder = os.path.abspath('.') + os.sep + "excelfile"
    # importFiles(pathFolder, ".xls", 0)
    main(pathFolder)
'''

