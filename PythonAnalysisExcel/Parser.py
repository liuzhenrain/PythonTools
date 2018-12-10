#/usr/bin/env python
# encoding: UTF-8
'''
Created on 2014年5月6日

@author: Administrator
'''
import xlrd,os,sys

def parseValue(vType, value):
    if vType == 'int' and value == '':
        value = 0
    elif vType == 'int' and value <> '':
        value = int(float(value))
    elif vType == 'float' and value == '':
        value = float(0)
    elif vType == 'float' and value <> '':
        value = float(value)
    return value

def GetCellData(table, row, col):
    if row > table.nrows or col > table.ncols:
        return ""
    dataType = table.cell_type(row, col)
    if dataType == xlrd.XL_CELL_TEXT:
        return table.cell_value(row, col).encode('utf-8')
    else:
        return str(table.cell_value(row, col))
    
def genErl(sheet):
    allRows = ""
    allRows +="%%----------------------------------------------------------------------\n"
    allRows +="%% ecode.hrl (自动生成，请勿编辑!)\n"
    allRows +="%%----------------------------------------------------------------------\n"
    for i in range(4, sheet.nrows):
        if GetCellData(sheet, i, 0) <> "" :
            key = parseValue('int',GetCellData(sheet, i, 0))
            line = "-define(%s, %s). %%%s\n" % (GetCellData(sheet, i, 1), key, GetCellData(sheet, i, 2))
#             print line
            allRows += line
    return allRows

def genCs(sheet):
    allRows = ""
    # allRows +="//----------------------------------------------------------------------\n"
    # allRows +="// SysECodeConst (自动生成，请勿编辑!)\n"
    # allRows +="//----------------------------------------------------------------------\n"
    # allRows +="using System;\n"
    # allRows +="using System.Collections.Generic;\n"
    # allRows +="namespace Assets.Scripts.Com.Game.Config\n"
    # allRows +="{\n"
    # allRows +="    [Serializable]\n"
    allRows +="\n    public class SysECodeConst\n"
    allRows +="    {\n"

    for i in range(4, sheet.nrows):
        if GetCellData(sheet, i, 0) <> "" :
            key = parseValue('int',GetCellData(sheet, i, 0))
            line = "        public const int %s = %s; //%s\n" % (GetCellData(sheet, i, 1), key, GetCellData(sheet, i, 2))
#             print line
            allRows += line
    allRows +="    }\n"
    # allRows +="}\n"
    return allRows

def main(xlsFile):
    '''
    '''
    
    if not os.path.isfile(xlsFile):
        print u'找不到文件 %s' % xlsFile
        raw_input()
        exit()

    xlsData = xlrd.open_workbook(xlsFile,formatting_info = True,encoding_override="utf-8")
    sheet = xlsData.sheet_by_name(u'ecode')  # 第一张表
    print u"生成hrl文件"
    erlData = genErl(sheet)

    hrlFile = open("ecode.hrl", 'w')      
    hrlFile.write(erlData)
    hrlFile.close()
    print u"生成ecode.hrl成功"

    print u"生成SysECodeConst.cs文件"
    csData = genCs(sheet)

    csFile = open("SysECodeConst.cs", 'w')      
    csFile.write(csData)
    csFile.close()
    print u"SysECodeConst.cs成功"
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        print u"错误码生成工具：\n把ecode.xls文件拖进来,回车确认"
        path = raw_input()
    main(path)