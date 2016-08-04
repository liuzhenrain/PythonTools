# coding: utf-8
"""
Created on 2016/7/26
@author: liuzhenrain
"""

from __future__ import division

import os
import glob
# import AnalysisExcel
from AnalysisExcel import *
import DataAccess

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


def main(folderPath):
    fileList = glob.glob1(folderPath, "*.xls")

    for item in fileList:
        excel_data_dic = readexcel(item)
        DataAccess.SaveToSqlite(excel_data_dic)
        # exit()
    return 0


if __name__ == "__main__":
    # 指定excel文件的位置
    # os.path.abspath('.') 会找到当前py文件的文件夹路径
    # os.sep 确定当前系统的路径分隔符，可以使用 print os.sep 打印看一下
    pathFolder = os.path.abspath('.') + os.sep + "excelfile"
    # importFiles(pathFolder, ".xls", 0)
    main(pathFolder)