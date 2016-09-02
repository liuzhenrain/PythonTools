#!/usr/bin/env python
# coding: utf-8
"""
@Author : Liuzhenrain
@Create : 16/8/4
"""
import sqlite3
import traceback
import LogCtrl

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
    for keyName in excel_data_dic.keys():
        # keyname 即为表名
        create_sql_command = "create table `%s` (`rowindex` integer primary key," % keyName
        # 确定EXCEL导入SQL中占用列的个数
        sql_table_ncols = 1  # 所有的表，默认有一个rowindex列

        # 以下数据结构请参照 AnalysisExcel中的_read_excel_data 方法注释
        excel_dic = {}
        excel_dic = excel_data_dic[keyName]
        field_dic = {}
        field_dic = excel_dic["fielddic"]  # field_dic:{fieldname,fieldtype}
        # 这里全TMD是地址，等于是指针，修改了field_name_array就等于修改了field_dic["fieldname"]里面的值，更加修改excel_data_dic里面的原始值。
        field_name_array = field_dic["fieldname"]
        allcolumns = []
        allcolumns.extend(field_name_array)
        field_type = []
        field_type.extend(field_dic["fieldtype"])
        # 确定表中是否需要unikey
        has_unikey = False
        export_type = field_dic["exporttype"]
        has_unikey, keycount = check_unikey(export_type)
        if has_unikey:
            create_sql_command += " `unikey` text,"
            print u"%s表有unikey,且拼合列总数为:%s" % (keyName, keycount)
            # 有unikey列，列总数加上一行
            sql_table_ncols += 1
            allcolumns.append("unikey")
        sql_table_ncols += len(field_name_array)
        # print sql_table_ncols

        field_name_len = len(field_name_array)
        for i in range(field_name_len):
            field_name = str(field_name_array[i])
            create_sql_command += ("`" + field_name + "` text")
            if i < field_name_len - 1:
                create_sql_command += ","
        create_sql_command += ");"

        # 首先查询数据库中有没有这个指定的表
        # 下条语句会返回一个sql语句回来，如果能够查询到指定的表名数据
        cursor.execute("select sql from sqlite_master where name='%s' and type='table';" % keyName)
        sql_all = cursor.fetchall()
        # 如果sql_all的长度大于零，代表有指定的表。
        if len(sql_all) > 0:
            # print "查询到有%s表" % (keyName)
            # 查询到了指定的表，那就可以开始进行数据比对工作
            # 首先比对列数以及列名是否均一致
            cursor.execute("PRAGMA table_info('%s');" % keyName)
            sql_all = cursor.fetchall()
            if len(sql_all) <> sql_table_ncols or check_field_column(sql_all, allcolumns):
                # 查询出来的列数不一致,或者列名有改变，先删除表，然后创建表
                try:
                    # 1.创建一个临时表：
                    sql1 = "CREATE TABLE sqlitestudio_temp_table AS SELECT * FROM `%s`;" % keyName
                    cursor.execute(sql1)
                    # 2.删除原始表:
                    sql2 = "DROP TABLE `%s`;" % keyName
                    cursor.execute(sql2)
                    # 3.创建一个新的表，表名和原始表一样，字段使用新字段。
                    sql3 = "CREATE TABLE `%s` (rowindex INTEGER PRIMARY KEY,"
                    # 3.1 循环读取excel中所有的列名,默认是不包括rowindex的。而且unikey是在数组最后一个
                    for index in range(len(allcolumns)):
                        field_name = str(allcolumns[index])
                        coltype = "TEXT"
                        if index < len(field_type):
                            coltype = parse_col_type(field_type[index])
                        sql3 += ("`" + field_name + "` %s" % coltype)
                        if index < len(allcolumns) - 1:
                            sql3 += ","
                    sql3 += ");"
                    # 4 使用Insert语句，将整个表的数据从临时表中copy到新表中
                    sql4 = "INSERT INTO `%s` (rowindex,"
                    for index in range(len(allcolumns)):
                        field_name = str(allcolumns[index])
                        sql3 += ("`" + field_name + "`")
                        if index < len(allcolumns) - 1:
                            sql3 += ","
                    # 删除表
                    if log_sql_command:
                        sql_command_array.append("drop table `%s`;" % (keyName))
                    cursor.execute("drop table `%s`;" % (keyName))
                    # 创建表
                    # print "创建表", sqlcommand
                    cursor.execute(create_sql_command)
                    if log_sql_command:
                        sql_command_array.append(create_sql_command)
                    command_array = get_add_sqlcommand(keyName, excel_dic, has_unikey, keycount)
                    cursor.executescript("".join(command_array))
                    conn.commit()
                except:
                    print traceback.format_exc()
                    LogCtrl.log(traceback.format_exc())
                    conn.rollback()
            else:
                # print "列数一致，并且列名都一致，进行数据比对"
                cursor.execute("select count(*) from %s;" % (keyName))
                values = cursor.fetchone()
                count = values[0]
                if count == 0:
                    # 表中无数据，产生insert语句
                    command_array = get_add_sqlcommand(keyName, excel_dic, has_unikey, keycount)
                    try:
                        cursor.executescript("".join(command_array))
                        conn.commit()
                    except:
                        print traceback.format_exc()
                        LogCtrl.log(traceback.format_exc())
                        conn.rollback()
                else:
                    # print "数据表中有数据", count
                    # 数据表中有数据，对每行数据进行比对，通过rowindex,如果EXCEL中有但是数据库中没有，会自动生成insert语句
                    command_array = get_update_command(keyName, excel_dic, has_unikey, keycount)
                    if len(command_array) > 0:
                        try:
                            cursor.executescript("".join(command_array))
                            conn.commit()
                        except:
                            print traceback.format_exc()
                            LogCtrl.log(traceback.format_exc())
                            conn.rollback()
                    # 删除在EXCEL中没有但是数据库中有的指定行号的数据
                    command_array = get_delete_command(keyName, excel_dic, has_unikey, keycount)
                    if len(command_array) > 0:
                        try:
                            cursor.executescript("".join(command_array))
                            conn.commit()
                        except:
                            print traceback.format_exc()
                            LogCtrl.log(traceback.format_exc())
                            conn.rollback()
        else:
            # print "没有查询到%s 表" % (keyName)
            # 创建表
            try:
                # print "创建表", sqlcommand
                if log_sql_command:
                    sql_command_array.append(create_sql_command)
                cursor.execute(create_sql_command)
                conn.commit()
                command_array = get_add_sqlcommand(keyName, excel_dic, has_unikey, keycount)
                cursor.executescript("".join(command_array))
                conn.commit()
            except:
                print traceback.format_exc()
                LogCtrl.log(traceback.format_exc())
                conn.rollback()
    cursor.close()
    _close_connection()
    return sql_command_array


def get_add_sqlcommand(tablename, excel_data_dic={}, has_unikey=False, keycount=0):
    global sql_command_array
    global log_sql_command
    command_array = []
    # print "开始产生数据库增加语句"
    sqlcommand = "insert into %s (rowindex," % tablename
    field_dic = {}
    field_dic = excel_data_dic["fielddic"]  # field_dic:{fieldname,fieldtype}
    field_name_array = field_dic["fieldname"]
    field_name_len = len(field_name_array)
    for i in range(field_name_len):
        field_name = str(field_name_array[i])
        sqlcommand += ("`" + field_name + "`")
        if i < field_name_len - 1:
            sqlcommand += ","
    if has_unikey:
        sqlcommand += ",`unikey`) values("
    else:
        sqlcommand += ") values("
    origin_command = sqlcommand
    data_dic = excel_data_dic["datadic"]
    for key in data_dic.keys():
        # 默认key就是rowindex值
        data_array = data_dic[key]
        sqlcommand += (str(key) + ",")
        for index in range(len(data_array)):
            sqlcommand += ("'" + str(data_array[index]) + "'")
            if index < len(data_array) - 1:
                sqlcommand += ","
        if has_unikey:
            unikey_array = []
            for i in range(keycount):
                unikey_array.append(str(data_array[i]))
            sqlcommand += (",'" + "_".join(unikey_array) + "'")
        sqlcommand += ");"
        command_array.append(sqlcommand)
        if log_sql_command:
            sql_command_array.append(sqlcommand)
        # 将语句恢复到进入循环之前的状态
        sqlcommand = origin_command
    return command_array


def get_single_add_command(tablename, field_name_array, rowindex, data_array, has_unikey, keycount):
    global sql_command_array
    global log_sql_command
    # print "开始产生数据库增加语句"
    sqlcommand = "insert into %s (rowindex," % tablename
    field_name_len = len(field_name_array)
    for i in range(field_name_len):
        field_name = str(field_name_array[i])
        # if field_name == "index":
        #     field_name = "e_index"
        sqlcommand += ("`" + field_name + "`")
        if i < field_name_len - 1:
            sqlcommand += ","
    if has_unikey:
        sqlcommand += ",`unikey`) values("
    else:
        sqlcommand += ") values("
    origin_command = sqlcommand
    sqlcommand += (str(rowindex) + ",")
    for index in range(len(data_array)):
        sqlcommand += ("'" + str(data_array[index]) + "'")
        if index < len(data_array) - 1:
            sqlcommand += ","
    if has_unikey:
        unikey_array = []
        for i in range(keycount):
            unikey_array.append(str(data_array[i]))
        sqlcommand += (",'" + "_".join(unikey_array) + "'")
    sqlcommand += ");"
    if log_sql_command:
        sql_command_array.append(sqlcommand)
    return sqlcommand


def get_update_command(tablename, excel_data_dic={}, has_unikey=False, keycount=0):
    global sql_command_array
    global log_sql_command
    command_array = []
    data_dic = excel_data_dic["datadic"]
    field_name_array = (excel_data_dic["fielddic"])["fieldname"]
    cursor = _get_connection().cursor()
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
            dic = data_dic[key]
            command_array.append(
                get_single_add_command(tablename, field_name_array, key, dic, has_unikey, keycount))

    # 获取指定表的所有列名字出来
    cursor.execute("PRAGMA table_info('%s');" % (tablename))
    sql_all = cursor.fetchall()
    sql_columns = []
    for row in sql_all:
        sql_columns.append(row[1].encode("utf-8"))

    origin_command = sql_command = "update `%s` set " % tablename
    for key in data_dic.keys():
        if key in exist_keys:
            continue
        cursor.execute("select * from `%s` where `rowindex` = '%s'" % (tablename, key))
        rowdata = cursor.fetchone()  # 查询到的数据行数据
        rowdataDic = {}
        for index in range(1, len(rowdata)):
            rowdataDic[sql_columns[index]] = unicode(rowdata[index]).encode("utf-8")

        # if rowdata == None: # 没有找到对应rowindex的数据
        excel_row_data = data_dic[key]  # excel当中的行数据

        excel = ""
        sql = ""
        command = ""

        if has_unikey:
            unikeyarray = []
            for i in range(keycount):
                unikeyarray.append(str(excel_row_data[i]))
            excel = "_".join(unikeyarray)
            sql = rowdata[1]
            if cmp(str(excel), sql.encode("utf-8")) != 0:
                command += "`unikey`='%s'," % excel
        for index in range(0, len(excel_row_data)):
            excel = excel_row_data[index]
            # excel = "".join(str(excel).split("  "))
            field_name = field_name_array[index];
            sql = rowdataDic[field_name]
            # if field_name == "description":
            #     print type(excel), type(sql)
            #     print "对比：", str(excel), sql
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
    return command_array


def get_delete_command(tablename, excel_data_dic={}, has_unikey=False, keycount=0):
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
