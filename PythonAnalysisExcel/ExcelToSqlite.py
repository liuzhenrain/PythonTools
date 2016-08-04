# coding: utf-8
"""
Created on 2016/7/26
@author: liuzhenrain
"""

from __future__ import division

import xlrd
import os
import glob

# Excel存储目录
pathFolder = ""

commentRow = 0
exportTypeRow = 1  # 输出类型所在行
fieldTypeRow = 2
fieldNameRow = 3
dataStartRow = 4
listSep = '^'


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
    sheetDatas = {}
    # 将所有为导出类型为S（服务端使用）列数给记录下来。
    for i in range(0, colCount):
        value = str(mainSheet.cell_value(exportTypeRow, i))
        if value == "s":
            serverData[i] = value

    # 记录所有的列名
    colNameArray = []
    for i in range(0, colCount):
        if not serverData.has_key(i):
            value = str(mainSheet.cell_value(fieldNameRow, i))
            colNameArray.append(value)
    sheetDatas["colname"] = colNameArray

    for rowIndex in range(dataStartRow, rowCount):
        rowValueArray = []
        if get_cell_data(mainSheet, rowIndex, 0) == "":
            print "%s表的第%s行KEY值是空的" % (sheetname, rowIndex + 1)
            continue
        for colIndex in range(0, colCount):
            if not serverData.has_key(colIndex):
                value = get_cell_data(mainSheet, rowIndex, colIndex)
                if value == "":
                    value = "\"\""
                rowValueArray.append(value)
        sheetDatas[str(rowIndex)] = rowValueArray

    print len(sheetDatas)


def main(folderPath):
    fileList = glob.glob1(folderPath, "*.xls")
    for item in fileList:
        readexcel(item)
        # exit()
    return 0


if __name__ == "__main__":
    # 指定excel文件的位置
    # os.path.abspath('.') 会找到当前py文件的文件夹路径
    # os.sep 确定当前系统的路径分隔符，可以使用 print os.sep 打印看一下
    pathFolder = os.path.abspath('.') + os.sep + "excelfile"
    # importFiles(pathFolder, ".xls", 0)
    main(pathFolder)
