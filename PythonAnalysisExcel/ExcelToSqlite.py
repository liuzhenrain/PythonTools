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
import LogCtrl
import time

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


def savetosqlite(folderPath, modifyList=[], logsql=False):
    has_db = False
    if not os.path.exists("steelray.db"):
        has_db = False
    else:
        has_db = True
    if has_db == False:
        logsql = has_db

    print logsql, has_db

    fileList = []
    if len(modifyList) <= 0 and has_db:
        return
    if len(modifyList) <= 0 or (not has_db):
        fileList = glob.glob1(folderPath, "*.xls")
    else:
        for fileinfo in modifyList:
            fileList.append(os.path.split(fileinfo["name"])[1])
    sql_command_array = []
    sql_count = 0
    threads = []
    t1 = threading.Thread(target=create_macro_file, args=(folderPath,))
    threads.append(t1)
    t1.start()
    ticks = int(time.time())
    for item in fileList:
        # if not item.__contains__("action_speed_test"):
        #     continue
        excel_data_dic = readexcel(item)
        t2 = threading.Thread(target=create_csfile, args=(folderPath + os.sep + "Structs", excel_data_dic,))
        threads.append(t2)
        t2.start()
        sql_command_array = DataAccess.SaveToSqlite("steelray.db", excel_data_dic, logsql)
        # 防止第一次导入数据库时生成超大SQL文件
        if logsql and len(sql_command_array) > 0:
            create_command_file(has_db, ticks, sql_command_array)
        sql_count += len(sql_command_array)
        sql_command_array = []
    print u"查询语句总条数:", sql_count
    LogCtrl.write_log_file()
    for item in threads:
        item.join()


def only_create_csfile(folderPath):
    fileList = glob.glob1(folderPath, "*.xls")
    threads = []
    t1 = threading.Thread(target=create_macro_file, args=(folderPath,))
    threads.append(t1)
    t1.start()
    for item in fileList:
        excel_data_dic = readexcel(item)
        t2 = threading.Thread(target=create_csfile, args=(folderPath + os.sep + "Structs", excel_data_dic,))
        threads.append(t2)
        t2.start()
    LogCtrl.write_log_file()
    for item in threads:
        item.join()

# if __name__ == "__main__":
#     # 指定excel文件的位置
#     # os.path.abspath('.') 会找到当前py文件的文件夹路径
#     # os.sep 确定当前系统的路径分隔符，可以使用 print os.sep 打印看一下
#     pathFolder = os.path.abspath('.') + os.sep + "excelfile"
#     savetosqlite(pathFolder)
#     # only_create_csfile(pathFolder)
