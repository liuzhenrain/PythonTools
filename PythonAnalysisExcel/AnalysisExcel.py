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


def _get_cell_data(sheet, row, col):
    if row > sheet.nrows or col > sheet.ncols:
        return ""
    datatype = sheet.cell_type(row, col)
    if datatype == xlrd.XL_CELL_TEXT:
        return sheet.cell_value(row, col).encode('utf-8')
    else:
        return str(sheet.cell_value(row, col))


# 读取excel数据，会返回一个字典。
# 字典数据组成，key:mainsheet,value:{fieldDic:{fieldName:fieldType},dataDic:{rowIndex:array}}
#              key:[subsheetname],value:{fieldDic:{fieldName:fieldType},dataDic:{rowIndex:array}}

def _read_excel_data(workbook, filename, sheetname, ismain, excel_data_dic={}):
    # 此字典用于保存所有的数据,数据结构参照方法注释

    sheet_data_dic = {}
    try:
        worksheet = workbook.sheet_by_name(sheetname)
    except:
        if ismain == True:
            print "文件名%s和主表名%s字不一致，请修改EXCEL文件" % (filename, sheetname)
            return excel_data_dic
        else:
            print "Excel文件:%s中没有%s这个表" % (filename, sheetname)
            return excel_data_dic
    colcount = worksheet.ncols
    rowcount = worksheet.nrows
    # dicKey = "mainsheet"
    # if not ismain:
    dicKey = sheetname

    fieldDic = {}  # 记录所有的字段名以及字段类型
    for colIndex in range(0, colcount):
        exportType = _get_cell_data(worksheet, exportTypeRow, colIndex)
        if exportType.lower() == "s":
            continue
        else:
            fieldType = _get_cell_data(worksheet, fieldTypeRow, colIndex)
            value = _get_cell_data(worksheet, fieldNameRow, colIndex)
            fieldDic[str(fieldType)] = value
            if fieldType[0] + fieldType[-1] == '[]':
                fieldType = fieldType[1:-1]
            if fieldType <> "int" and fieldType.lower() <> "string" and fieldType <> "float":
                excel_data_dic = _read_excel_data(workbook, filename, fieldType, False, excel_data_dic)
    # 将字段信息记录到字典中
    sheet_data_dic["fieldDic"] = fieldDic

    # 获取实际数据
    data_dic = {}
    for rowIndex in range(dataStartRow, rowcount):
        rowdata = []
        dataKey = _get_cell_data(worksheet, rowIndex, 0)
        # 如果表中的第一个数据key为空值，直接跳过。
        if dataKey == "":
            print "%s表第%s行Key数据为空，直接跳过." % (sheetname, rowIndex + 1)
            continue
        for colIndex in range(0, colcount):
            fieldType = _get_cell_data(worksheet, exportTypeRow, colIndex)
            if fieldType.lower() == "s":
                continue
            else:
                value = _get_cell_data(worksheet, rowIndex, colIndex)
                rowdata.append(value)
        data_dic[rowIndex - dataStartRow] = rowdata

    sheet_data_dic["datadic"] = data_dic

    excel_data_dic[dicKey] = sheet_data_dic
    return excel_data_dic


def readexcel(filename):
    print ".......当前EXCEL : ", filename, "......."
    pathFolder = os.path.abspath('.') + os.sep + "excelfile"
    # 获取整个工作簿
    workbook = xlrd.open_workbook(pathFolder + os.sep + filename, formatting_info=True, encoding_override="utf-8")
    excel_data_dic = {}
    main_sheet_name = str(filename).replace(".xls", "")
    excel_data_dic = _read_excel_data(workbook, filename, main_sheet_name, True, excel_data_dic)
    print "获得的数据KEYS个数:%s" % len(excel_data_dic.keys())
    return excel_data_dic
