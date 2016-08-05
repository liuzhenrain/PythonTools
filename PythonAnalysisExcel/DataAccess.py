# coding: utf-8
"""
@Author : Liuzhenrain
@Create : 16/8/4
"""
import sqlite3

dataName = ""
connection = None


def SaveToSqlite(databaseName, excel_data_dic={}):
    global dataName
    dataName = databaseName
    conn = _get_connection()
    cursor = conn.cursor()
    for keyName in excel_data_dic.keys():
        # keyname 即为表名
        sqlcommand = "create table %s (rowindex integer primary key," % keyName
        # 以下数据结构请参照 AnalysisExcel中的_read_excel_data 方法注释
        excel_dic = {}
        excel_dic = excel_data_dic[keyName]
        field_dic = {}
        field_dic = excel_dic["fielddic"]  # field_dic:{fieldname,fieldtype}
        field_name_array = field_dic["fieldname"]
        export_type = field_dic["exporttype"]
        field_name_len = len(field_name_array)
        for i in range(field_name_len):
            sqlcommand += (str(field_name_array[i])+" text")
            if i < field_name_len - 1:
                sqlcommand += ","
        sqlcommand += ");"
        # sqlcommand = sqlcommand % field_dic.keys()
        print sqlcommand
        # try:
        #     # cursor.execute("create table %s (rowindex integer primary key);" % (keyName))
        #     cursor.execute(sqlcommand,field_dic.keys())
        #     print "数据库创建%s表成功" % (keyName)
        # except:
        #     print "数据库中已经有了%s表" % (keyName)
    conn.commit()
    cursor.close()
    _close_connection()


def _get_connection():
    global connection
    connection = sqlite3.connect(dataName)
    return connection


def _close_connection():
    global connection
    if connection <> None:
        connection.close()
