#!/usr/bin/env python
# coding: utf-8
"""
@Author : Liuzhenrain
@Create : 16/8/4
"""
import sqlite3
import traceback
import LogCtrl
import copy

import time

dataName = ""
connection = None
log_sql_command = False
# 记录所有的SQL操作语句（增删改），并且将其写入到文件当中
sql_command_array = []


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


def check_field_column(columns, fields):
    # 原始的EXCEL表中没有rowindex列，这里默认加上去。
    if len(columns) != len(fields) + 1:
        return True
    for row in columns:
        name = row[1]
        if cmp(name, 'rowindex') == 0:
            continue
        if not (name in fields):
            return True
    return False


def parse_col_type(col_type):
    if col_type == "int" or col_type == "float" or col_type == "string":
        return col_type
    else:
        return "TEXT"


def SaveToSqlite(databaseName, excel_data_dic={}, return_command=False):
    global dataName
    dataName = databaseName
    conn = _get_connection()
    cursor = conn.cursor()
    # 记录所有的SQL操作语句（增删改），并且将其写入到文件当中
    global sql_command_array
    global log_sql_command
    log_sql_command = return_command
    sql_command_array = []
    for tablename,data in excel_data_dic.iteritems():
        # keyname 即为表名
        create_sql_command = "create table `%s` (`rowindex` INT PRIMARY KEY," % tablename
        # 确定EXCEL导入SQL中占用列的个数
        sql_table_ncols = 1  # 所有的表，默认有一个rowindex列

        # 以下数据结构请参照 AnalysisExcel中的_read_excel_data 方法注释
        excel_dic = {}
        # 深层COPY重新开辟一个内存空间，保存所有的数据，然后新的变量指向新开辟的地址，防止改变原有的数据。
        excel_dic = copy.deepcopy(data)
        field_dic = {}
        field_dic = excel_dic["fielddic"]  # field_dic:{fieldname,fieldtype}
        # 这里全TMD是地址，等于是指针，修改了field_name_array就等于修改了field_dic["fieldname"]里面的值，更加修改excel_data_dic里面的原始值。
        field_name_array = field_dic["fieldname"]
        excel_allcolumns = []
        excel_allcolumns.extend(field_name_array)
        excel_allfieldtype = []
        excel_allfieldtype.extend(field_dic["fieldtype"])

        field_name_len = len(field_name_array)
        for i in range(field_name_len):
            sql_field_name = str(field_name_array[i])
            excel_type = str(excel_allfieldtype[i])
            sql_field_type = excel_type
            if excel_type != "int" and excel_type != "float":
                sql_field_type = "TEXT"
            create_sql_command += "`%s` %s" % (sql_field_name, sql_field_type.upper())
            if i < field_name_len - 1:
                create_sql_command += ","
        create_sql_command += ");"

        # 首先查询数据库中有没有这个指定的表
        # 下条语句会返回一个sql语句回来，如果能够查询到指定的表名数据
        cursor.execute("select sql from sqlite_master where name='%s' and type='table';" % tablename)
        sql_all = cursor.fetchall()
        # 如果sql_all的长度大于零，代表有指定的表。
        if len(sql_all) > 0:
            # print "查询到有%s表" % (keyName)
            # 查询到了指定的表，那就可以开始进行数据比对工作
            # 首先比对列数以及列名是否均一致
            cursor.execute("PRAGMA table_info('%s');" % tablename)
            sql_all = cursor.fetchall()
            if len(sql_all) != len(excel_allcolumns) + 1 or check_field_column(sql_all, excel_allcolumns):
                print u"数据库表：%s 查询出来的列数不一致,或者列名有改变，先删除表，然后创建表" % tablename
                try:
                    # 删除表
                    if log_sql_command:
                        sql_command_array.append("drop table `%s`;" % tablename)
                    cursor.execute("drop table `%s`;" % tablename)
                    # 创建表
                    cursor.execute(create_sql_command)
                    conn.commit()
                    if log_sql_command:
                        sql_command_array.append(create_sql_command)
                    excute_add_sqlcommand(tablename, excel_dic)
                except:
                    LogCtrl.log("创建表 %s 的时候出错，数据库执行语句:\n %s \n 错误信息:\n %s \n" % (tablename, create_sql_command, traceback.format_exc()))
                    conn.rollback()
            else:
                # print "列数一致，并且列名都一致，进行数据比对"
                cursor.execute("select count(*) from %s;" % (tablename))
                values = cursor.fetchone()
                count = values[0]
                if count == 0:
                    # 表中无数据，产生insert语句
                    excute_add_sqlcommand(tablename, excel_dic)
                else:
                    # print "数据表中有数据", count
                    # 数据表中有数据，对每行数据进行比对，通过rowindex,如果EXCEL中有但是数据库中没有，会自动生成insert语句
                    excute_update_command(tablename, excel_dic)
                    # 删除在EXCEL中没有但是数据库中有的指定行号的数据
                    command_array = get_delete_command(tablename, excel_dic)
                    if len(command_array) > 0:
                        try:
                            cursor.executescript("".join(command_array))
                            conn.commit()
                        except:
                            LogCtrl.log("删除表 %s 的时候出现错误。执行语句:\n %s \n 错误信息: \n %s" % (tablename,"".join(command_array), traceback.format_exc()))
                            conn.rollback()
        else:
            print u"没有查询到%s 表" % tablename,
            # 创建表
            try:
                # print "创建表", sqlcommand
                if log_sql_command:
                    sql_command_array.append(create_sql_command)
                cursor.execute(create_sql_command)
                conn.commit()
                # start = time.time()
                excute_add_sqlcommand(tablename, excel_dic)
                # cursor.executescript("".join(command_array))
                # conn.commit()
                # end = time.time()
                # print u"写入表 %s 数据耗时：%s" % (tablename, (end - start))
            except:
                LogCtrl.log("创建表 %s 的时候出错，数据库执行语句:\n %s \n 错误信息:\n %s \n" % (tablename, create_sql_command, traceback.format_exc()))
                conn.rollback()
    cursor.close()
    _close_connection()
    return sql_command_array


def excute_add_sqlcommand(tablename, excel_data_dic={}):
    print u"对 %s 表执行添加数据操作" % tablename,

    start = time.time()
    global sql_command_array
    global log_sql_command
    conn = _get_connection()
    cursor = conn.cursor()
    command_array = []
    # print "开始产生数据库增加语句"
    sqlcommand = "REPLACE INTO %s (rowindex," % tablename
    field_dic = {}
    field_dic = excel_data_dic["fielddic"]  # field_dic:{fieldname,fieldtype}
    field_name_array = field_dic["fieldname"]
    field_name_len = len(field_name_array)
    for i in range(field_name_len):
        field_name = str(field_name_array[i])
        sqlcommand += ("`" + field_name + "`")
        if i < field_name_len - 1:
            sqlcommand += ","
    # sqlcommand += ") values("
    sqlcommand += ") values "
    origin_command = sqlcommand
    data_dic = excel_data_dic["datadic"]
    values_array = []
    for key in data_dic.keys():
        values = "(%s," % key
        data_array = data_dic[key]
        for index in range(len(data_array)):
            values += ("'" + str(data_array[index]) + "'")
            if index < len(data_array) - 1:
                values += ","
        values += ")"
        values_array.append(values)
    sqlcommand = "%s %s;" % (sqlcommand, ",".join(values_array))
    command_array.append(sqlcommand)
    if len(values_array) <= 0:
        cursor.close()
        conn.close()
        print u"无数据需要添加"
        return
    try:
        cursor.execute(sqlcommand)
        conn.commit()
        if log_sql_command:
            sql_command_array.append(sqlcommand)
        sqlcommand = ""
    except:
        LogCtrl.log("对表 %s 进行数据写入的时候出错，请检查错误信息 \n %s" % (tablename, traceback.format_exc()))
        conn.rollback()
    end = time.time()
    print u"耗时：%s" % (end - start)
    cursor.close()
    conn.close()
    return command_array


def excute_update_command(tablename, excel_data_dic={}):
    print u"开始对 %s 表进行更新操作" % tablename,
    start = time.time()
    global sql_command_array
    global log_sql_command
    data_dic = excel_data_dic["datadic"]
    excel_allcolumans = []
    excel_allcolumans.extend((excel_data_dic["fielddic"])["fieldname"])
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("select `rowindex` from %s" % tablename)
    # sql_rowindex_list 返回的数据是一个list类型的里面的数据全部是tuple类型的数据
    sql_rowindex_list = cursor.fetchall()
    count = len(data_dic.keys())
    exist_keys = []
    # 找出所有在excel中有但是sqlite数据库中没有的行号，并将其存储起来
    for i in range(count):
        key = data_dic.keys()[i]
        tupleitem = (key,)
        if not (tupleitem in sql_rowindex_list):
            exist_keys.append(key)
    sql_command = "REPLACE INTO `%s`" % tablename
    command_columms = "(`rowindex`,"
    sql_columns = []
    for item in excel_allcolumans:
        sql_columns.append("`%s`" % item)
    command_columms = "%s %s) VALUES " % (command_columms, ",".join(sql_columns))
    command_value_array = []
    if len(exist_keys) > 0:
        command_temp = "%s %s" % (sql_command, command_columms)
        for key in exist_keys:
            excel_row_data = data_dic[key]  # excel当中的行数据
            command_values = "(%s," % key
            # excel_row_data中有非str的数据，所以不能直接用.join方法，需要更改
            strvalues = []
            for item in excel_row_data:
                # if type(item) == str:
                #     strvalues.append("'%s'" % item)
                # else:
                    strvalues.append("'%s'" % str(item))
            command_values = "%s %s)" % (command_values, ",".join(strvalues))
            command_value_array.append(command_values)
        command_temp = "%s %s;" % (command_temp, ",".join(command_value_array))
        if len(command_value_array) > 0:
            try:
                cursor.execute(command_temp)
                conn.commit()
                if log_sql_command:
                    sql_command_array.append(command_temp)
            except:
                # print traceback.format_exc()
                LogCtrl.log("对表 %s 进行新数据写入时出错，请检查错误信息以及EXCEL数据\n数据库操作语句: %s \n错误信息:\n %s" % (
                tablename, command_temp, traceback.format_exc()))
                conn.rollback()
        command_temp = None
    command_value_array = []  # 用完了将它恢复成没有数据的状态。
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `%s`;" % tablename)
    sql_all_data = cursor.fetchall()
    sql_all_dic = {}
    for item in sql_all_data:
        rowindex = item["rowindex"]
        sql_all_dic[rowindex] = item
    del sql_all_data
    # 遍历每一行EXCEL数据，和数据库进行数据比对,然后拼合成一条replace语句。
    for key in data_dic.keys():
        excel_row_data = data_dic[key]  # excel当中的行数据
        if key in exist_keys:
            continue
        # cursor.execute("select * from `%s` where `rowindex` = '%s'" % (tablename, key))
        rowdata = sql_all_dic[key]  # 查询到的数据行数据
        for index in range(0, len(excel_row_data)):
            excel = excel_row_data[index]
            field_name = excel_allcolumans[index]
            sql = unicode(rowdata[field_name]).encode("utf-8")
            if cmp(str(excel), sql) != 0:
                # print "出现对比数据,字段:%s,Excel数据：%s Sqlite数据:%s" % (field_name, excel, sql)
                # 只要出现一个数据不一样，之后就不管了，直接更新整行数据，并且跳去当前的循环体
                command_values = "(%s," % key  # 第一个是rowindex行
                # excel_row_data中有非str的数据，所以不能直接用.join方法，需要更改
                strvalues = []
                for item in excel_row_data:
                    # if type(item) == str:
                    #     strvalues.append("'%s'" % item)
                    # else:
                    strvalues.append("'%s'" % str(item))
                command_values = "%s %s)" % (command_values, ",".join(strvalues))
                command_value_array.append(command_values)
                break
    # 数据比较结束，开始进行数据库存储
    sql_command = "%s %s %s;" % (sql_command, command_columms, ",".join(command_value_array))
    if len(command_value_array) <= 0:
        print u"没有数据需要更新"
        cursor.close()
        conn.close()
        return
    try:
        cursor.execute(sql_command)
        conn.commit()
        if log_sql_command:
            sql_command_array.append(sql_command)
        end = time.time()
        print u"耗时：%s" % (end - start)
    except:
        LogCtrl.log("对表 %s 进行数据更新时出错，请检查错误信息以及EXCEL数据\n数据库操作语句: %s \n错误信息:\n %s" % (
        tablename, command_temp, traceback.format_exc()))
        conn.rollback()
    cursor.close()
    conn.close()


def get_update_command(tablename, excel_data_dic={}):
    global sql_command_array
    global log_sql_command
    command_array = []
    data_dic = excel_data_dic["datadic"]
    field_name_array = (excel_data_dic["fielddic"])["fieldname"]
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("select `rowindex` from %s" % tablename)
    # sql_rowindex_list 返回的数据是一个list类型的里面的数据全部是tuple类型的数据
    sql_rowindex_list = cursor.fetchall()
    count = len(data_dic.keys())
    exist_keys = []
    for i in range(count):
        key = data_dic.keys()[i]
        tupleitem = (key,)
        if not (tupleitem in sql_rowindex_list):
            exist_keys.append(key)

    if len(exist_keys) > 0:
        sql_command = "REPLACE INTO `%s`"
        command_columms = "(rowindex,"
        command_columms = "%s %s) " % (command_columms, ",".join(field_name_array))
        sql_command = "%s %s" % (sql_command, command_columms)
        command_value_array = []
        for key in exist_keys:
            excel_row_data = data_dic[key]  # excel当中的行数据
            command_values = "(%s," % key
            command_values = "%s %s)" % (command_values, ",".join(excel_row_data))
            command_value_array.append(command_values)
        sql_command = "%s %s" % (sql_command, ",".join(command_value_array))
        try:
            cursor.execute(sql_command)
            conn.commit()
            if log_sql_command:
                sql_command_array.append(sql_command)
        except:
            print traceback.format_exc()
            conn.rollback()
            print "写入新数据的时候出错，EXCEL表名:" % tablename

    # 获取指定表的所有列名字出来
    cursor.execute("PRAGMA table_info('%s');" % (tablename))
    sql_all = cursor.fetchall()
    sql_columns = []
    for row in sql_all:
        sql_columns.append(row[1].encode("utf-8"))

    origin_command = sql_command = "update `%s` set " % tablename
    for key in data_dic.keys():
        excel_row_data = data_dic[key]  # excel当中的行数据
        if key in exist_keys:
            continue
        cursor.execute("select * from `%s` where `rowindex` = '%s'" % (tablename, key))
        rowdata = cursor.fetchone()  # 查询到的数据行数据
        rowdataDic = {}
        for index in range(1, len(rowdata)):
            rowdataDic[sql_columns[index]] = unicode(rowdata[index]).encode("utf-8")

        excel = ""
        sql = ""
        command = ""

        for index in range(0, len(excel_row_data)):
            excel = excel_row_data[index]
            field_name = field_name_array[index]
            sql = rowdataDic[field_name]
            if cmp(str(excel), sql) != 0:
                # print "出现对比数据,字段:%s,Excel数据：%s Sqlite数据:%s" % (field_name, excel, sql)
                command += "`%s`='%s'," % (field_name, excel)
        if len(command) != 0:
            command = command[0:-1]
            sql_command += command
            sql_command += " where `rowindex` = %s;" % key
            command_array.append(sql_command)
            if log_sql_command:
                sql_command_array.append(sql_command)
        # print sql_command
        sql_command = origin_command
    cursor.close()
    conn.close()
    return command_array


def get_delete_command(tablename, excel_data_dic={}):
    global sql_command_array
    global log_sql_command
    command_array = []
    origincommand = sqlcommand = "delete from `%s` where `rowindex`=" % tablename
    data_dic = excel_data_dic["datadic"]
    cursor = _get_connection().cursor()
    cursor.execute("select count(*) from `%s`;" % tablename)
    excute_data = cursor.fetchone()
    if len(data_dic.keys()) == excute_data[0]:
        return command_array
    cursor.execute("select `rowindex` from `%s`;" % tablename)
    for item in cursor:
        rowindex = item[0]
        if not data_dic.has_key(rowindex):
            sqlcommand += "'%s';" % rowindex
            if log_sql_command:
                sql_command_array.append(sqlcommand)
            command_array.append(sqlcommand)
        sqlcommand = origincommand
    return command_array


def _get_connection():
    global connection
    connection = sqlite3.connect(dataName)
    return connection


def _close_connection():
    global connection
    if connection <> None:
        connection.close()
