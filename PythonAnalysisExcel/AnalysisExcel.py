# coding: utf-8
"""
@Author : Liuzhenrain
@Create : 16/8/3
"""
import xlrd
import os

commentRow = 0
exportTypeRow = 1  # 输出类型所在行
fieldTypeRow = 2
fieldNameRow = 3
dataStartRow = 4
listSep = '^'

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