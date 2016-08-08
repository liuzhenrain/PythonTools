# coding: utf-8
"""
@Author : Liuzhenrain
@Create : 16/8/4
"""
import sqlite3
import traceback

dataName = ""
connection = None


def SaveToSqlite(databaseName, excel_data_dic={}):
    global dataName
    dataName = databaseName
    conn = _get_connection()
    cursor = conn.cursor()
    # 记录所有的SQL操作语句（增删改），并且将其写入到文件当中
    sql_command_array=[]
    for keyName in excel_data_dic.keys():
        # keyname 即为表名

        sqlcommand = "create table %s (rowindex integer primary key," % keyName
        # 确定EXCEL导入SQL中占用列的个数
        sql_table_ncols = 1  # 所有的表，默认有一个rowindex列

        # 以下数据结构请参照 AnalysisExcel中的_read_excel_data 方法注释
        excel_dic = {}
        excel_dic = excel_data_dic[keyName]
        field_dic = {}
        field_dic = excel_dic["fielddic"]  # field_dic:{fieldname,fieldtype}
        field_name_array = field_dic["fieldname"]
        # 确定表中是否需要unikey
        export_type = field_dic["exporttype"]
        if export_type[0] == "k" and export_type[1] == "k":
            sqlcommand += " unikey text,"
            # 有unikey列，列总数加上一行
            sql_table_ncols += 1
        sql_table_ncols += len(field_name_array)
        # print sql_table_ncols

        field_name_len = len(field_name_array)
        for i in range(field_name_len):
            field_name = str(field_name_array[i]).lower()
            if field_name == "index":
                field_name = "e_index"
            sqlcommand += (field_name + " text")
            if i < field_name_len - 1:
                sqlcommand += ","
        sqlcommand += ");"

        # 首先查询数据库中有没有这个指定的表
        # 下条语句会返回一个sql语句回来，如果能够查询到指定的表名数据
        cursor.execute("select sql from sqlite_master where name='%s' and type='table';" % keyName)
        sql_all = cursor.fetchall()
        if len(sql_all) > 0:
            print "查询到有%s表" % (keyName)
            # 查询到了指定的表，那就可以开始进行数据比对工作
            # 首先比对列数是否一致。
            cursor.execute("PRAGMA table_info('%s');" % (keyName))
            sql_all = cursor.fetchall()
            if len(sql_all) <> sql_table_ncols:
                print "数据库表%s的列数和Excel数据应写入的列数%s不一致" % (len(sql_all), sql_table_ncols)
                # 查询出来的列数不一致，先删除表，然后创建表
                try:
                    # 删除表
                    sql_command_array.append("drop table %s;" % (keyName))
                    cursor.execute("drop table %s;" % (keyName))
                    # 创建表
                    print "创建表", sqlcommand
                    cursor.execute(sqlcommand)
                    sql_command_array.append(sqlcommand)
                    conn.commit()
                except:
                    print traceback.format_exc()
                    conn.rollback()
            else:
                print "列数一致，进行数据比对"
        else:
            print "没有查询到%s 表" % (keyName)
            # 创建表
            try:
                print "创建表", sqlcommand
                sql_command_array.append(sqlcommand)
                cursor.execute(sqlcommand)
                conn.commit()
            except:
                print traceback.format_exc()
                conn.rollback()

        # field_name_len = len(field_name_array)
        # for i in range(field_name_len):
        #     sqlcommand += (str(field_name_array[i]) + " text")
        #     if i < field_name_len - 1:
        #         sqlcommand += ","
        # sqlcommand += ");"
        # sqlcommand = sqlcommand % field_dic.keys()
        # print sqlcommand


        # try:
        #     # cursor.execute("create table %s (rowindex integer primary key);" % (keyName))
        #     cursor.execute(sqlcommand)
        #     conn.commit()
        #     print "数据库创建%s表成功" % (keyName)
        # except:
        #     print "数据库中已经有了%s表,%s" % (keyName)
        #     cursor.execute("PRAGMA table_info('%s');" % (keyName))
        #     print "影响行数：", cursor.rowcount,"证明有这么多个列"
        #     if cursor.rowcount <> sql_table_ncols:
        #         print "查询到的字段数%s,不等于当前获取的EXCEL行数%s" % (cursor.rowcount,sql_table_ncols)
        #     else:
        #         print "查询到的字段数%s,等于当前获取的EXCEL行数%s" % (cursor.rowcount, sql_table_ncols)
        #     conn.commit()
    cursor.close()
    _close_connection()


def get_add_sqlcommand(excel_data_dic={},sql_command_array=[]):
    print "开始产生数据库增加语句"
    # 不添加列名，保证数据对齐就行了。第一行是rowindex，Int类型
    sqlcommand = "insert into %s values("



def _get_connection():
    global connection
    connection = sqlite3.connect(dataName)
    return connection


def _close_connection():
    global connection
    if connection <> None:
        connection.close()
