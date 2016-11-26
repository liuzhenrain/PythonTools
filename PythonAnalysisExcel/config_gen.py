# /usr/bin/env python
# encoding: UTF-8
'''
Created on 2014年5月6日

@author: Administrator
'''

import xml.dom.minidom
import xlrd
import glob
import os, sys
from __builtin__ import len
import ExcelToSqlite

macroFile = 'macro.config'
commentRow = 0
exportTypeRow = 1  # 输出类型所在行
fieldTypeRow = 2
fieldNameRow = 3
dataStartRow = 4
listSep = '^'
erlPath = ''
csPath = ''
xmlPath = ''
log_sqlcommand = False


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


def GetCellData(table, row, col):
    if row > table.nrows or col > table.ncols:
        return ""
    dataType = table.cell_type(row, col)
    if dataType == xlrd.XL_CELL_TEXT:
        return table.cell_value(row, col).encode('utf-8')
    else:
        return str(table.cell_value(row, col))


def getXlsData(path):
    '''
    打开xls文件
    '''
    xlsData = xlrd.open_workbook(path, formatting_info=True,
                                 encoding_override="utf-8")
    return xlsData


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


def getStruct(xlsData, sheetName, isMain=True, sFieldDict={}, cFieldDict={}, sDefDict={}, cDefDict={}):
    '''
    生成客户端、后端结构
    '''
    try:
        sheet = xlsData.sheet_by_name(sheetName)
    except:
        print u'子表%s不存在' % sheetName
        exit()
    colCount = sheet.ncols

    sDefName = 'sys_%s' % sheetName
    sDefDict[sDefName] = ''
    sFieldDict[sheetName] = []
    # cFieldDict[sheetName] = []

    for col in range(colCount):
        value = str(sheet.cell_value(exportTypeRow, col))
        if value == 'k':
            sFieldDict[sheetName].append(col)
            # cFieldDict[sheetName].append(col)
        elif value == 'a':
            sFieldDict[sheetName].append(col)
            # cFieldDict[sheetName].append(col)
            # elif value == 'c':
            # cFieldDict[sheetName].append(col)
        elif value == 's':
            sFieldDict[sheetName].append(col)

    # # 生成record
    recTxt = "-record(" + sDefName + ", {\n"
    sLen = len(recTxt) - 1
    space = ' ' * sLen
    sItemLen = len(sFieldDict[sheetName])

    for i in range(sItemLen):
        prop = sFieldDict[sheetName][i]
        fieldName = GetCellData(sheet, fieldNameRow, prop)
        fieldType = GetCellData(sheet, fieldTypeRow, prop)
        if fieldType[0] + fieldType[-1] == '[]':
            fieldType = fieldType[1:-1]

        if fieldType <> 'int' and fieldType <> 'string' and fieldType <> 'float':
            # # 递归生成复杂结构的数据
            sFieldDict, cFieldDict, sDefDict, cDefDict = getStruct(xlsData, fieldType, False, sFieldDict, cFieldDict,
                                                                   sDefDict, cDefDict)
        if i + 1 == sItemLen:
            line = "%s%s %%%s\n" % (space, fieldName, GetCellData(sheet, commentRow, prop))
        else:
            line = "%s%s, %%%s\n" % (space, fieldName, GetCellData(sheet, commentRow, prop))
        recTxt += line
    recTxt += "}).\n"
    sDefDict[sDefName] += recTxt

    #     csTxt = '\
    #     [Serializable]\n\
    #     public class %s\n\
    #     {\n\
    # %s\
    # %s\
    #     }\n\
    # '
    #     cDefName = 'Sys%s' % sheetName
    #     if isMain:
    #         line = '%s		public %s %s;\n' % ('', 'string', 'unikey')
    #     else:
    #         line = ''
    #     cItemLen = len(cFieldDict[sheetName])
    #     constructorLines = ''  # # 构造函数
    #     for i in range(cItemLen):
    #         prop = cFieldDict[sheetName][i]
    #         fieldName = GetCellData(sheet, fieldNameRow, prop)
    #         fieldType = GetCellData(sheet, fieldTypeRow, prop)
    #
    #         isList = fieldType[0] + fieldType[-1] == '[]'
    #         if isList:
    #             fieldType = fieldType[1:-1]
    #
    #         if fieldType <> 'int' and fieldType <> 'string' and fieldType <> 'float':
    #             # # 递归生成复杂结构的数据
    #             sFieldDict, cFieldDict, sDefDict, cDefDict = getStruct(xlsData, fieldType, False, sFieldDict, cFieldDict,
    #                                                                    sDefDict, cDefDict)
    #             fieldType = 'Sys%s' % fieldType
    #         if isList:
    #             line = '%s		public List<%s> %s; //%s\n' % (
    #                 line, fieldType, fieldName, GetCellData(sheet, commentRow, prop))
    #         else:
    #             line = '%s		public %s %s; //%s\n' % (line, fieldType, fieldName, GetCellData(sheet, commentRow, prop))
    #
    #         constructorLines = '%s			this.%s = instance.%s;\n' % (constructorLines, fieldName, fieldName)
    #
    #     constructorLines = '		public %s(){}\n		public %s(%s instance)\n		{\n%s		}\n' % (
    #         cDefName, cDefName, cDefName, constructorLines)
    #     constructorLines = ''
    #     csTxt = csTxt % (cDefName, line, constructorLines)
    #     cDefDict[cDefName] = csTxt
    return sFieldDict, cFieldDict, sDefDict, cDefDict


def exportDef(path, sDefDict, cDefDict):
    '''
    输出定义文件
    '''
    sSysList = {}
    sContent = ""
    sysSFile = '%s%ssys.hrl' % (erlPath, os.sep)
    if os.path.exists(sysSFile):
        sysSFiler = open(sysSFile, 'r')
        sContent = sysSFiler.read()
        sContent = sContent.replace("%% coding: latin-1\n", "")
    splitSContents = sContent.split("}).\n") if len(sContent) > 0 else []

    for splitSContent in splitSContents:
        if len(splitSContent) > 0:
            sysSKey = splitSContent.split(", {")[0][8:]
            splitSContent = splitSContent + "}).\n"
            sysSInfo = {
                "sys_s_key": sysSKey,
                "content": splitSContent
            }
            sSysList[sysSKey] = sysSInfo

    for sDefkey in sDefDict.keys():
        if len(sDefDict[sDefkey]) > 0:
            sysSInfo = {
                "sys_s_key": sDefkey,
                "content": sDefDict[sDefkey][:-1] + "\n"
            }
            sSysList[sDefkey] = sysSInfo

    tSysSList = []
    for sSysKey in sSysList:
        tSysSList.append(sSysList[sSysKey])

    tSysSList = sorted(tSysSList, lambda (x), (y): cmp(x['sys_s_key'], y['sys_s_key']), reverse=False)
    sysSFileW = open(sysSFile, 'w')

    print u'生成hrl',
    allSTxt = "%% coding: latin-1\n"
    for tSys in tSysSList:
        allSTxt += tSys['content']
    sysSFileW.write(allSTxt)
    sysSFileW.close()
    print u'服务端配置文件ok'

    csTxt = '/**\n\
*%s  自动生成,请勿编辑\n\
*/\n\
\n\
using System;\n\
using System.Collections.Generic;\n\
namespace Assets.Scripts.Com.Game.Config\n\
{\n\
%s\
}\n\
'
    print u'生成Packet.cs',
    cSysList = {}
    cContent = ""
    cSysFile = os.path.abspath('.') + os.sep + '\Packet.cs'
    if os.path.exists(cSysFile):
        cContent = open(cSysFile, 'r').read()
        cContent = cContent[133:-2]

    splitFlag = '}\n'
    splitcContents = cContent.split(splitFlag) if len(cContent) > 0 else []

    for splitcContent in splitcContents:
        if len(splitcContent) > 0:
            splitcContent2 = splitcContent.split("public class ")
            if len(splitcContent2) > 1:
                splitcContent3 = splitcContent2[1]
                splitcContent4 = splitcContent3.split("{\n")[0]
                sysCKey = splitcContent4.split("\n")[0]
                splitcContent = splitcContent + "}\n"
                packetInfo = {
                    "sys_c_key": sysCKey,
                    "content": splitcContent
                }
                cSysList[sysCKey] = packetInfo

    print u'生成cs文件',
    for cDefKey in cDefDict.keys():
        # csFile = open('%s%s%s.cs' % (csPath, os.sep, cDefKey), 'w')
        # txt = csTxt % (cDefKey, cDefDict[cDefKey])
        if cSysList.has_key(cDefKey):
            sysCInfo = cSysList[cDefKey]
            sysCInfo['content'] = cDefDict[cDefKey]
            cSysList[cDefKey] = sysCInfo
        else:
            sysCInfo = {
                "sys_c_key": cDefKey,
                "content": cDefDict[cDefKey]
            }
            cSysList[cDefKey] = sysCInfo
            # csFile.write(txt)
            # csFile.close()
        #
    print u'客户端常量配置'
    (_erlMacro, csMacro) = genMacro(path)
    for macroKey in csMacro.keys():
        if cSysList.has_key(macroKey):
            sysCInfo = cSysList[macroKey]
            sysCInfo['content'] = csMacro[macroKey]
            cSysList[macroKey] = sysCInfo
        else:
            sysCInfo = {
                "sys_c_key": macroKey,
                "content": csMacro[macroKey]
            }
            cSysList[macroKey] = sysCInfo
    print u'客户端常量配置ok'


# cSysList2 = []
# for cSysKey in cSysList:
#     cSysList2.append(cSysList[cSysKey])
# cSysList2 = sorted(cSysList2, lambda (x), (y): cmp(x['sys_c_key'], y['sys_c_key']), reverse=False)
# allTxt = ""
# for cSys in cSysList2:
#     allTxt += cSys['content']
#
# csFile = open(cSysFile, 'w')
# txt = csTxt % ('Packet', allTxt[1:])
# csFile.write(txt)
# csFile.close()
# print u'客户端配置文件ok'


def initIndexRow(xlsData, sheetName, isMain=True, indexRowDict={}):
    '''
    生成字表index对应的所在行
    '''
    try:
        sheet = xlsData.sheet_by_name(sheetName)
    except:
        print u'子表%s不存在' % sheetName
        exit()

    colCount = sheet.ncols
    for col in range(colCount):
        exportType = str(sheet.cell_value(exportTypeRow, col))
        if exportType == 'a' or exportType == 's' or exportType == 'c':
            # # 只有a s c才会复杂结构
            fieldType = str(sheet.cell_value(fieldTypeRow, col))
            if fieldType[0] + fieldType[-1] == '[]':
                # # 去掉表示数组的中括号
                fieldType = fieldType[1:-1]

            if fieldType <> 'int' and fieldType <> 'string' and fieldType <> 'float':
                '''
                如果是复杂类型
                递归去获取index对应的行数
                '''
                indexRowDict = initIndexRow(xlsData, fieldType, False, indexRowDict)
    if not isMain:
        '''
        主表不用生成index-row
        '''
        rowCount = sheet.nrows
        indexRowDict[sheetName] = {}
        for row in range(dataStartRow, rowCount):
            '''
            逐行
            '''
            index = GetCellData(sheet, row, 0)
            if index <> '':
                if indexRowDict[sheetName].has_key(index):
                    print u'生成失败！\n子表%s的行%d与%d重复index' % (sheetName, indexRowDict[sheetName][index], row)
                    exit()
                index = parseValue('int', index)
                indexRowDict[sheetName][int(index)] = row
    return indexRowDict


def sformat(sData, xlsData, fieldType, value, sFieldDict, indexRowDict):
    if fieldType == '[int]' or fieldType == '[float]':
        # # int数组
        if value == '':
            sData = '%s[],' % sData
        else:
            values = value.split(listSep)
            sData += '['
            for v in values:
                sData = '%s%d,' % (sData, parseValue(fieldType[1:-1], v))
            sData = '%s],' % sData[:-1]
    elif fieldType == 'int' or fieldType == 'float':
        sData = '%s%s,' % (sData, parseValue(fieldType, value))
    elif fieldType == '[string]':
        # # 字符串数组
        if value == '':
            sData = '%s[],' % sData
        else:
            values = value.split(listSep)
            sData += '['
            for v in values:
                sData = '%s<<"%s">>,' % (sData, parseValue(fieldType[1:-1], v))
            sData = '%s],' % sData[:-1]
    elif fieldType == 'string':
        sData = '%s<<"%s">>,' % (sData, parseValue(fieldType, value))
    else:
        # # 其它数据结构
        isList = fieldType[0] + fieldType[-1] == '[]'
        if value == '' and isList:
            sData = '%s[],' % sData
        elif value == '' and not isList:
            sData = '%sundefined,' % sData
        else:
            if not isList:
                value = int(float(value))
                temp = parseSSubData(xlsData, fieldType, int(value), sFieldDict, indexRowDict)
                sData = '%s%s,' % (sData, temp)
            else:
                fieldType = fieldType[1:-1]
                sData += '['
                for v in value.split(listSep):
                    v = int(float(v))
                    temp = parseSSubData(xlsData, fieldType, v, sFieldDict, indexRowDict)
                    sData = '%s%s,' % (sData, temp)
                sData = '%s],' % sData[:-1]
    return sData


def parseSSubData(xlsData, sheetName, index, sFieldDict={}, indexRowDict={}):
    try:
        sheet = xlsData.sheet_by_name(sheetName)
    except:
        print u'子表%s不存在' % sheetName
        exit()
    row = indexRowDict[sheetName][index]
    sData = '{sys_%s,' % sheetName
    for col in sFieldDict[sheetName]:
        exportType = GetCellData(sheet, exportTypeRow, col)
        value = GetCellData(sheet, row, col)
        fieldType = str(sheet.cell_value(fieldTypeRow, col))
        value = parseValue(fieldType, value)
        if exportType == 'k':
            # # 拼成key
            sData = '%s%s,' % (sData, value)
        elif exportType == 's':
            sData = sformat(sData, xlsData, fieldType, value, sFieldDict, indexRowDict)
        elif exportType == 'a':
            sData = sformat(sData, xlsData, fieldType, value, sFieldDict, indexRowDict)
    sData = '%s}' % sData[:-1]
    # print sData
    return sData


def newElement(document, name, value):
    element = document.createElement(name)
    elementValue = document.createTextNode(str(value))
    element.appendChild(elementValue)
    return element


def newElements(document, elementsName, elementType, values):
    elements = document.createElement(elementsName)
    for v in values:
        elements.appendChild(newElement(document, elementType, parseValue(elementType, v)))
    return elements


def parseCSubData(xlsData, fileName, sheetName, document, index, cFieldDict, indexRowDict):
    try:
        sheet = xlsData.sheet_by_name(sheetName)
    except:
        print u'子表%s不存在' % sheetName
        exit()
    if not indexRowDict[sheetName].has_key(index):
        print u'%s不存在index为%s的数据' % (sheetName, index)
        exit()
    row = indexRowDict[sheetName][index]
    sub_node = document.createElement(fileName)
    for col in cFieldDict[sheetName]:
        exportType = GetCellData(sheet, exportTypeRow, col)
        value = GetCellData(sheet, row, col)
        fieldType = str(sheet.cell_value(fieldTypeRow, col))
        fieldName = str(sheet.cell_value(fieldNameRow, col))
        if exportType == 'c' or exportType == 'a' or exportType == 'k':
            sub_node = cformat(xlsData, document, sub_node, fieldType, fieldName, value, cFieldDict, indexRowDict)
    return sub_node


def cformat(xlsData, document, sub_node, fieldType, fieldName, value, cFieldDict, indexRowDict):
    if fieldType == 'int' or fieldType == 'float':
        value = parseValue(fieldType, value)
        sub_node.appendChild(newElement(document, fieldName, value))
    elif fieldType == '[int]' or fieldType == '[string]' or fieldType == '[float]':
        if value <> '':
            values = value.split(listSep)
            sub_node.appendChild(newElements(document, fieldName, fieldType[1:-1], values))
    elif fieldType == 'string':
        sub_node.appendChild(newElement(document, fieldName, value))
    elif value == '':
        return sub_node
    else:
        # # 其它数据结构
        isList = fieldType[0] + fieldType[-1] == '[]'
        if not isList:
            value = int(float(value))
            sub_node.appendChild(
                parseCSubData(xlsData, fieldName, fieldType, document, value, cFieldDict, indexRowDict))
        else:
            elements = document.createElement(fieldName)
            for v in value.split(listSep):
                v = int(float(v))
                elements.appendChild(
                    parseCSubData(xlsData, 'Sys%s' % fieldType[1:-1], fieldType[1:-1], document, v, cFieldDict,
                                  indexRowDict))
            sub_node.appendChild(elements)
    return sub_node


def parseData(path, xlsData, sheetName, isMain=True, sFieldDict={}, cFieldDict={}, indexRowDict={}):
    '''
    生成数据
    '''
    try:
        sheet = xlsData.sheet_by_name(sheetName)
    except:
        print u'子表%s不存在' % sheetName
        exit()
    if isMain:
        '''
        主表
        '''

        # # 后端
        erltxt = "%" * 2 + " coding: latin-1\n"
        erltxt += "%" * 3 + "-" * 50 + "\n" + "%" * 3 + "  自动生成,请勿编辑\n" + "%" * 3 + "-" * 50 + "\n"
        erltxt += '-module(sys_%s).\n' % sheetName
        erltxt += '-include("wg_log.hrl").\n'
        erltxt += "-compile(export_all).\n"
        sKey = ''
        sData = '{sys_%s,' % sheetName
        allKeys = ''

        # minidom = xml.dom.minidom
        # cKey = ''
        # cDefName = 'Sys%s' % sheetName
        # doc = minidom.Document()
        # root_node = doc.createElement('ArrayOfSys%s' % sheetName)
        # root_node.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        # root_node.setAttribute('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')
        # doc.appendChild(root_node)

        for row in range(dataStartRow, sheet.nrows):
            # # 逐行遍历
            emptyKey = False

            # # 客户端
            for col in sFieldDict[sheetName]:
                exportType = GetCellData(sheet, exportTypeRow, col)
                value = GetCellData(sheet, row, col)
                fieldType = str(sheet.cell_value(fieldTypeRow, col))
                if exportType == 'k':
                    # # 拼成key
                    if len(value) == 0 or emptyKey:
                        emptyKey = True
                        print u'\n%s第%d行的key值为空，该行被忽略' % (sheetName, row)
                        break
                    value = parseValue(fieldType, value)
                    if sKey == '':
                        sKey = '%s%s,' % (sKey, value)
                        # cKey = '%s_' % value
                    elif sKey[0] == '{':
                        sKey = '%s%s,' % (sKey, value)
                        # cKey = '%s%s_' % (cKey, value)
                    else:
                        sKey = '{%s%s,' % (sKey, value)
                        # cKey = '%s%s_' % (cKey, value)
                    sData = '%s%s,' % (sData, value)
                elif exportType == 's':
                    sData = sformat(sData, xlsData, fieldType, value, sFieldDict, indexRowDict)
                elif exportType == 'a':
                    sData = sformat(sData, xlsData, fieldType, value, sFieldDict, indexRowDict)
            if emptyKey:
                continue
            if sKey[0] == '{':
                sKey = '%s}' % sKey[:-1]
            else:
                sKey = '%s' % sKey[:-1]
            sData = '%s}' % sData[:-1]
            allKeys = '%s%s,' % (allKeys, sKey)
            erltxt += 'get(%s) -> %s;\n' % (sKey, sData)
            sKey = ''
            sData = '{sys_%s,' % sheetName

            # cKey = cKey[:-1]
            # sub_node = doc.createElement(cDefName)

            # if isMain:
            # # 主节点添加unikey
            # sub_node.appendChild(newElement(doc, 'unikey', cKey))

            # for col in cFieldDict[sheetName]:
            #     exportType = GetCellData(sheet, exportTypeRow, col)
            #     value = GetCellData(sheet, row, col)
            #     fieldType = str(sheet.cell_value(fieldTypeRow, col))
            #     fieldName = str(sheet.cell_value(fieldNameRow, col))
            #     value = parseValue(fieldType, value)
            #     if exportType == 'k':
            #         sub_node.appendChild(newElement(doc, fieldName, value))
            #         continue
            #     else:
            #         sub_node = cformat(xlsData, doc, sub_node, fieldType, fieldName, value, cFieldDict, indexRowDict)
            #
            # root_node.appendChild(sub_node)

            cKey = ''
        erltxt += 'get(_Id) -> ?ERROR("data not exist:~w", [_Id]), throw({error, 20}).\n'
        if len(allKeys) > 0:
            allKeys = 'list() -> [%s].\n' % allKeys[:-1]
        else:
            allKeys = 'list() -> [].\n'
        erltxt += allKeys
        h = open('%s%sserver%ssys_%s.erl' % (path, os.sep, os.sep, sheetName), 'w')
        h.write(erltxt)
        h.close()
        # # 客户端
        # xml_f = open('%s%s%s.xml' % (xmlPath, os.sep, sheetName), 'w')
        # doc.writexml(xml_f, addindent='  ', newl='\n', encoding='utf-8')


def main(path, logsql):
    timeFile = os.path.abspath('.') + os.sep + '\last_time.txt'
    dirPath = path + r'\\*.xls'
    strTimeInfos = ""
    timeInfos = {}
    modifyList = []
    if os.path.exists(timeFile):
        strTimeInfos = open(timeFile, 'r').read()
    timeInfoList = strTimeInfos.split("##\n")
    for strTimeInfo in timeInfoList:
        if len(strTimeInfo) > 0:
            timeArray = strTimeInfo.split(",")
            name = timeArray[0]
            time = timeArray[1]
            timeInfo = {'name': name, 'time': time}
            timeInfos[name] = timeInfo

    for file in glob.glob(dirPath):
        mtime = int(os.path.getmtime(file))
        strFile = os.path.split(file)
        fileName = strFile[1][:-4]
        fileInfo = {
            "name": file,
            "time": mtime
        }
        if timeInfos.has_key(fileName):
            timeInfo = timeInfos[fileName]
            baseTime = int(timeInfo['time'])
            if mtime > baseTime:
                modifyList.append(fileInfo)
                timeInfo['time'] = mtime
                timeInfos[fileName] = timeInfo
        else:
            modifyList.append(fileInfo)
            timeInfo = {'name': fileName, 'time': mtime}
            timeInfos[fileName] = timeInfo
    modifyList = sorted(modifyList, lambda (x), (y): cmp(x['time'], y['time']), reverse=True)
    # 生成客户端文件以及数据库文件。
    ExcelToSqlite.savetosqlite(path, modifyList, logsql)
    global erlPath, csPath, xmlPath
    erlPath = "%s%s%s" % (path, os.sep, "server")
    # csPath = "%s%s%s%s%s" % (path, os.sep, 'client', os.sep, 'cs')
    # xmlPath = "%s%s%s%s%s" % (path, os.sep, 'client', os.sep, 'xml')
    if not os.path.isdir(erlPath):
        os.makedirs(erlPath)
    # if not os.path.isdir(csPath):
    #     os.makedirs(csPath)
    # if not os.path.isdir(xmlPath):
    #     os.makedirs(xmlPath)

    sFieldDict = {}  # 后端用到的字段序号
    cFieldDict = {}  # 后端用到的字段序号
    sDefDict = {}  # 后端record字典
    cDefDict = {}  # 客户端定义字典
    print u'开始生成数据：'
    print u'xls目录：%s' % path

    for modifyFile in modifyList:
        filePath = modifyFile['name']
        temp = os.path.split(filePath)
        modifyFile = getXlsData(filePath)
        fileName = temp[1]
        mainSheet = fileName[:-4]
        print u'%s: 结构' % (fileName),
        sFieldDict, cFieldDict, sDefDict, cDefDict = getStruct(modifyFile, mainSheet, True, sFieldDict, cFieldDict,
                                                               sDefDict,
                                                               cDefDict)
        print u'ok, 子表索引',
        indexRowDict = initIndexRow(modifyFile, mainSheet)
        print u'ok, 数据',
        parseData(path, modifyFile, mainSheet, True, sFieldDict, cFieldDict, indexRowDict)
        print u'ok'
        # # 处理完一个要重置
        sFieldDict = {}  # 后端用到的字段序号
        cFieldDict = {}  # 后端用到的字段序号

    exportDef(path, sDefDict, cDefDict)
    print u'\n生成完成'
    print u'erl %s\server' % (path)
    print u'cs %s\client\cs' % (path)
    print u'xml %s\client\\xml' % (path)

    timeFile = open(timeFile, 'w')
    timeInfoList = []
    for key in timeInfos:
        timeInfo = timeInfos[key]
        timeInfoList.append(timeInfo)

    baseTimeStr = ""
    timeInfoList = sorted(timeInfoList, lambda (x), (y): cmp(x['name'], y['name']), reverse=False)
    for timeInfo in timeInfoList:
        name = timeInfo['name']
        time = timeInfo['time']
        base = str(name) + "," + str(time) + "##\n"
        baseTimeStr += base
    timeFile.write(baseTimeStr)
    timeFile.close()
    print u'\n持久操作时间ok'
    print u"\n 一定要打开当前文件夹下的log.log文件是否有错误信息，如果有请修改excel文件之后重新执行bat文件"


def genMacroContent(xlsFile, sheetName, valueIndex, erlIndex, csIndex, commentIndex, lang):
    xlsData = getXlsData(xlsFile)
    sheet = xlsData.sheet_by_name(sheetName)
    csContent = ''
    erlContent = ''
    erlContent += "%% coding: latin-1\n"
    erlContent += "%%----------------------------------------------------------------------\n"
    erlContent += "%% %s.hrl (%s.xls自动生成，请勿编辑!)\n" % (sheetName, sheetName)
    erlContent += "%%----------------------------------------------------------------------\n"
    csContent += "\n    public class Sys%sConst\n" % (capitalizeName(sheetName))
    csContent += "    {\n"
    valueType = GetCellData(sheet, 2, valueIndex)
    for i in range(4, sheet.nrows):
        macroValue = GetCellData(sheet, i, valueIndex)
        macroValue = parseValue(valueType, macroValue)
        comment = GetCellData(sheet, i, commentIndex)
        if csIndex >= 0:
            csMacro = GetCellData(sheet, i, csIndex)
            line = "        public const %s %s = %s; //%s\n" % (valueType, csMacro, macroValue, comment)
            csContent += line
        if erlIndex >= 0:
            erlMacro = GetCellData(sheet, i, erlIndex)
            line = "-define(%s, %s). %%%s\n" % (erlMacro, macroValue, comment)
            erlContent += line

    csContent += "    }\n"

    if erlIndex >= 0:
        hrlName = ''
        if len(lang) > 0:
            hrlName = '%s%s%s_%s.hrl' % (erlPath, os.sep, sheetName, lang)
        else:
            hrlName = '%s%s%s.hrl' % (erlPath, os.sep, sheetName)
        hrlFile = open(hrlName, 'w')
        hrlFile.write(erlContent)
        hrlFile.close()

    return (erlContent, csContent)


def genMacro(path):
    '''
    生成客户端和后端的hrl和常量数据
    '''
    global macroFile
    macroFile = '%s%s%s' % (path, os.sep, macroFile)
    erlMacroDict = {}
    csMacroDict = {}
    if os.path.isfile(macroFile):
        content = open(macroFile, 'r')
        lines = content.readlines()
        content.close()
        for line in lines:
            if line.find('#') == -1:
                config = line.split(',')
                xlsFile = '%s%s%s.xls' % (path, os.sep, config[0].strip())
                if os.path.isfile(xlsFile):
                    if len(config) >= 6:
                        lang = config[5].strip()
                    else:
                        lang = ''
                    sheetName = config[0].strip()  # 文件名，也是sheet表的名
                    sheetKey = "Sys%sConst" % (capitalizeName(sheetName))
                    valueIndex = int(config[1])  # 常量值在sheet表里面的列，从0开始
                    erlIndex = int(config[2])  # erl的宏名，在sheet表里面的列， -1表示不输出hrl文件
                    csIndex = int(config[3])  # cs的变量名，在sheet表里面的列， -1表示不输出到cs
                    commentIndex = int(config[4])  # 注释内容，在sheet表里面的列， -1表示不输出hrl文件
                    (erlContent, csContent) = genMacroContent(xlsFile, sheetName, valueIndex, erlIndex, csIndex,
                                                              commentIndex, lang)
                    if erlIndex >= 0:
                        erlMacroDict[sheetKey] = erlContent
                    if csIndex >= 0:
                        csMacroDict[sheetKey] = csContent
                else:
                    print u'错误  ====%s.xls 不存在====' % (config[0].strip())
    return (erlMacroDict, csMacroDict)


if __name__ == "__main__":
    logsql = False
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if len(sys.argv) >= 3:
            logsql = True if sys.argv[2]=="True" else False
        else:
            logsql = False
    else:
        path = '%s%s%s' % (os.path.abspath('.'), os.sep, 'excelfile')
    main(path, logsql)
