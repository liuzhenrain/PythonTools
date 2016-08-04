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


# 读取excel数据，会返回一个字典。
# 字典数据组成，key:mainsheet,value:{colname:array,dataDic:{data:array}}
#              key:[subsheetname],value:{colname:array,dataDic:{data:array}}

def read_excel_data(workbook, filename, sheetname, ismain, excel_data_dic={}):
    # 此字典用于保存所有的数据,数据结构参照方法注释

    sheet_data_dic = {}
    try:
        worksheet = workbook.sheet_by_name(sheetname)
    except:
        if ismain == True:
            print "文件名%s和主表名%s字不一致，请修改EXCEL文件" % (filename, sheetname)
            exit()
        else:
            print "Excel文件:%s中没有%s这个表" % (filename, sheetname)
            exit()
    colcount = worksheet.ncols
    rowcount = worksheet.nrows
    dicKey = "mainsheet"
    if not ismain:
        dicKey = sheetname

    colnames = []  # 记录所有的列名
    for colIndex in range(0, colcount):
        fieldType = get_cell_data(worksheet, exportTypeRow, colIndex)
        if fieldType.lower() == "s":
            continue
        else:
            value = get_cell_data(worksheet, fieldNameRow, colIndex)
            colnames.append(value)
    # 将列名记录到字典中
    sheet_data_dic["colname"] = colnames

    # 获取实际数据
    data_dic = {}
    for rowIndex in range(dataStartRow, rowcount):
        rowdata =[]
        dataKey = get_cell_data(worksheet, rowIndex, 0)
        # 如果表中的第一个数据key为空值，直接跳过。
        if dataKey == "":
            print "%s表第%s行Key数据为空，直接跳过." % (sheetname, rowIndex + 1)
            continue
        for colIndex in range(0, colcount):
            fieldType = get_cell_data(worksheet, exportTypeRow, colIndex)
            if fieldType.lower() == "s":
                continue
            else:
                value = get_cell_data(worksheet, rowIndex, colIndex)
                rowdata.append(value)
            print ""
        data_dic[rowIndex] = rowdata

    sheet_data_dic["datadic"] = data_dic

    excel_data_dic[dicKey] = sheet_data_dic


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
