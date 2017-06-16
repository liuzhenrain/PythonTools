# coding: utf-8
"""
@Author : Liuzhenrain
@Create : 16/8/3
"""
import os
import traceback

import xlrd

import LogCtrl

commentRow = 0
exportTypeRow = 1  # 输出类型所在行
fieldTypeRow = 2
fieldNameRow = 3
dataStartRow = 4


def capitalizeName(value):
    '''
    大写化字符串
    sys_config -> SysConfig
    config -> Config
    '''
    values = value.split('_')
    newValue = ''
    for v in values:
        newValue = '%s%s' % (newValue, v.capitalize())
    return newValue


def get_cell_data(sheet, row, col):
    if row > sheet.nrows or col > sheet.ncols:
        return ""
    datatype = sheet.cell_type(row, col)
    if datatype == xlrd.XL_CELL_TEXT:
        return sheet.cell_value(row, col).encode('utf-8')
    else:
        return str(sheet.cell_value(row, col))


def parseValue(vType, value):
    '''
    处理数据类型转换
    '''
    if vType == 'int' and value == '':
        value = 0
    elif vType == 'int' and value <> '':
        value = int(float(value))
    elif vType == 'float' and value == '':
        value = float(0)
    elif vType == 'float' and value <> '':
        value = float(value)
    return value


def check_unikey(export_type=[]):
    count = len(export_type)
    has_unikey = False
    keycount = 1
    for i in range(1, count):
        if str(export_type[i]).lower() == "k":
            has_unikey = True
            keycount += 1
        else:
            break
    return has_unikey, keycount


# 读取excel数据，会返回两个个字典。这个方法只会返回客户端保存到sqlite当中的数据，以及需要写入cs文件的相关信息
# sheet_data_dic 字典数据组成:
#           key:[heetname],value:{fieldDic:{fieldname:array,fieldtype:fieldType},dataDic:{rowIndex:array},exporttype:array}
# fieldDic 字典数据组成:
#           key:fieldname,value:Array
#           key:fieldtype,value:Array
#           key:exporttype,value:Array
#           key:fieldDesc,value:Array

def _read_excel_data(workbook, filename, sheetname, ismain, excel_data_dic={}):
    # 此字典用于保存所有的数据,数据结构参照方法注释

    sheet_data_dic = {}
    try:
        worksheet = workbook.sheet_by_name(sheetname)
    except:
        if ismain == True:
            LogCtrl.log("文件名%s和主表名%s字不一致，请修改EXCEL文件" % (filename, sheetname))
            return excel_data_dic
        else:
            LogCtrl.log("Excel文件:%s中没有%s这个表" % (filename, sheetname))
            return excel_data_dic
        print traceback.format_exc()
        exit()
    colcount = worksheet.ncols
    rowcount = worksheet.nrows
    real_data_col = []  # 包含有实际内容的列数据
    # dicKey = "mainsheet"
    # if not ismain:
    dicKey = sheetname

    fieldDic = {}  # 记录所有的字段名以及字段类型,去掉导出类型为S的部分
    field_name_array = []
    field_type_array = []
    export_type_array = []
    field_desc_array = []

    for colindex in range(colcount):
        exportType = get_cell_data(worksheet, exportTypeRow, colindex)
        if exportType.lower() == "s":
            continue
        # 除了第一列导出类型为n的保留，其他的都直接剔除
        if colindex > 0 and exportType.lower() == "n":
            continue
        fieldType = get_cell_data(worksheet, fieldTypeRow, colindex)
        fieldName = get_cell_data(worksheet, fieldNameRow, colindex)
        if fieldType == "" or fieldName == "":
            continue
        real_data_col.append(colindex)
    # if len(real_data_col) == 1:
    #     LogCtrl.log("Excel文件:%s %s表只有一个KEY值需要写入到客户端数据库,所以直接跳过。" % (filename, sheetname))
    #     return excel_data_dic
    for colIndex in real_data_col:
        exportType = get_cell_data(worksheet, exportTypeRow, colIndex)
        export_type_array.append(exportType)
        fieldType = get_cell_data(worksheet, fieldTypeRow, colIndex)
        fieldName = get_cell_data(worksheet, fieldNameRow, colIndex)
        fieldDesc = get_cell_data(worksheet, commentRow, colIndex)
        field_name_array.append(fieldName)
        field_type_array.append(fieldType)
        field_desc_array.append(fieldDesc)

        if fieldType[0] + fieldType[-1] == '[]':
            fieldType = fieldType[1:-1]
        if fieldType <> "int" and fieldType.lower() <> "string" and fieldType <> "float":
            excel_data_dic = _read_excel_data(workbook, filename, fieldType, False, excel_data_dic)
    # 判定是否有unikey列，如果有直接将unikey列，列名列类型写入到数组中，在其他地方就不用判定了（列类型一定为string)
    has_unikey, unikeycount = check_unikey(export_type_array)
    if has_unikey:
        print u"%s表有unikey,且拼合列总数为:%s AnalysisExcel.py 143" % (filename, unikeycount)
        field_name_array.append("unikey")
        field_type_array.append("string")
        field_desc_array.append("组合键")
        export_type_array.append("a")
    fieldDic["fieldname"] = field_name_array
    fieldDic["fieldtype"] = field_type_array
    fieldDic["fielddesc"] = field_desc_array
    fieldDic["exporttype"] = export_type_array
    # # 将字段信息记录到字典中
    sheet_data_dic["fielddic"] = fieldDic

    # 获取实际数据
    data_dic = {}
    for rowIndex in range(dataStartRow, rowcount):
        rowdata = []
        dataKey = get_cell_data(worksheet, rowIndex, 0)

        # 如果表中的第一个数据key为空值，直接跳过。
        if dataKey == "":
            print u"%s表第%s行Key数据为空，直接跳过." % (sheetname, rowIndex + 1)
            # LogCtrl.log("%s表第%s行Key数据为空，直接跳过." % (sheetname, rowIndex + 1))
            # for colIndex in real_data_col:
            #     value = "%s表第%s行Key数据为空,其余值全部填写同样的数据" % (sheetname, rowIndex + 1)
            #     rowdata.append(value)
            continue
        else:
            for colIndex in real_data_col:
                datatype = get_cell_data(worksheet, fieldTypeRow, colIndex)
                value = get_cell_data(worksheet, rowIndex, colIndex)
                value = parseValue(datatype, value)
                if datatype[0] + datatype[-1] == "[]" or (
                                    datatype != "float" and datatype != "int" and datatype != "string"):
                    value = value.split(".")[0]
                if sheetname == "vip":
                    print value
                # if datatype == "string":
                #     if not value.__contains__("[\n]"):
                #         value = value.replace("\n", "")
                #     if not value.__contains__("[\t]"):
                #         value = value.replace("\t", "")
                #     value = value.replace("\r", "")
                rowdata.append(value)
            if has_unikey:
                unikey_value = []
                for uniindex in range(unikeycount):
                    unikey_value.append(str(rowdata[uniindex]))
                rowdata.append("_".join(unikey_value))
        data_dic[rowIndex + 1] = rowdata

    sheet_data_dic["datadic"] = data_dic
    sheet_data_dic["ismain"] = ismain
    excel_data_dic[dicKey] = sheet_data_dic
    return excel_data_dic


def get_workbook(path):
    workbook = None
    if os.path.exists(path):
        try:
            workbook = xlrd.open_workbook(path, formatting_info=True, encoding_override="utf-8")
        except:
            print u"Path:%s不是UTF-8编码的，请改成UTF-8编码" % path
            print traceback.format_exc()
            exit()
    return workbook


def readexcel(filename):
    print u".......当前EXCEL : %s ......" % filename
    # LogCtrl.log(".......当前EXCEL : %s ......" % filename)
    pathFolder = os.path.abspath('.') + os.sep + "excelfile"
    # 获取整个工作簿
    workbook = get_workbook(pathFolder + os.sep + filename)
    # workbook = xlrd.open_workbook(pathFolder + os.sep + filename, formatting_info=True, encoding_override="utf-8")
    excel_data_dic = {}
    main_sheet_name = str(filename).replace(".xls", "")
    excel_data_dic = _read_excel_data(workbook, filename, main_sheet_name, True, excel_data_dic)
    # print "获得的数据KEYS个数:%s" % len(excel_data_dic.keys())
    return excel_data_dic
