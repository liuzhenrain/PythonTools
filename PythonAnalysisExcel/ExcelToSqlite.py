# coding: utf-8
"""
Created on 2016/7/26
@author: liuzhenrain
"""

from __future__ import division

import sqlite3
import xlrd
import os
import glob

# Excel存储目录
pathFolder = ""
# 定义一个全局的链接变量
connection = None

commentRow = 0
exportTypeRow = 1  # 输出类型所在行
fieldTypeRow = 2
fieldNameRow = 3
dataStartRow = 4
listSep = '^'


def importFiles(folderPath, wildcard, recursion):
    # getFileList 仅会返回一个列表,所以list就是一个数组列表了
    # list = getFileList(folderPath, wildcard, recursion)

    filePath = folderPath + r'\\*.xls'
    print glob.glob1(folderPath, "*.xls").__len__()

    return

    for item in list:
        readexcel(item)
    return

    dbCn = getConnection("steelray.db")

    # 执行EXCUTE语句,一定会返回一个光标回来,光标一定要遍历才行
    corsur = dbCn.execute("select * from weapon")

    # 数据库查询返回的光标必须要进行遍历才能正常拿到数据
    for row in corsur:
        print "ID = ", row[0]
        print "NAME = ", row[1], "\n"

    # 浮标和链接在使用过后都必须关闭
    corsur.close()
    dbCn.close()

    print list.__len__()


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


# Excel 操作部分   """
def get_cell_data(sheet, row, col):
    if row > sheet.nrows or col > sheet.ncols:
        return ""
    datatype = sheet.cell_type(row, col)
    if datatype == xlrd.XL_CELL_TEXT:
        return sheet.cell_value(row, col).encode('utf-8')
    else:
        return str(sheet.cell_value(row, col))


def readexcel(filename):
    print ".......当前EXCEL : ", filename, "......."
    global pathFolder
    # 获取整个工作簿
    workbook = xlrd.open_workbook(pathFolder + os.sep + filename, formatting_info=True, encoding_override="utf-8")
    sheetname = filename.split('.')[0]
    try:
        mainSheet = workbook.sheet_by_name(sheetname)
    except:
        print "EXCEL文件主表:%s和文件名:%s不一致" % (sheetname, filename)
        exit()
    # 记录行数和列数
    colCount = mainSheet.ncols
    rowCount = mainSheet.nrows
    serverData = {}
    print colCount
    # 将所有为导出类型为S（服务端使用）列数给记录下来。
    for i in range(0, colCount):
        value = str(mainSheet.cell_value(exportTypeRow, i))
        print i, value
        if value == "s":
            print "用于服务器的:", i, value
            serverData[i] = value

    print "%s:%d" % ("应用于服务器的行数", len(serverData))
    # 记录所有的列名
    sqlCommandArray = []  # 记录数据库操作语句
    sqlcommand = "insert into %s (" % (sheetname)
    colNameArray = []
    for i in range(0, colCount):
        if not serverData.has_key(i):
            value = str(mainSheet.cell_value(fieldNameRow, i))
            colNameArray.append(value)

    for rowIndex in range(dataStartRow, rowCount):
        origin = sqlcommand
        rowValueArray = []
        for colIndex in range(0, colCount):
            if not serverData.has_key(colIndex):
                value = get_cell_data(mainSheet, rowIndex, colIndex)
                if value == "":
                    value = "\"\""
                rowValueArray.append(value)
        sqlcommand = origin


# 以下为数据库部分 """
def getConnection(dbPath):
    global connection
    if connection == None:
        # 链接一个数据库,如果没有会自动创建,所以能够保证connection一定会被赋值
        connection = sqlite3.connect(dbPath)
    # 当isolation_level设置为None之后,以后对数据库进行操作会自动进行提交;否者为""
    # connection.isolation_level = None
    return connection


def close_db_connection():
    global connection
    if connection != None:
        connection.close()
        connection = None
    return 0


#    数据库部分结束

def main(folderPath):
    fileList = glob.glob1(folderPath, "*.xls")
    for item in fileList:
        readexcel(item)
        # exit()
    return 0


if __name__ == "__main__":
    # 制定excel文件的位置
    # os.path.abspath('.') 会找到当前py文件的文件夹路径
    # os.sep 确定当前系统的路径分隔符，可以使用 print os.sep 打印看一下
    pathFolder = os.path.abspath('.') + os.sep + "excelfile"
    # importFiles(pathFolder, ".xls", 0)
    main(pathFolder)
