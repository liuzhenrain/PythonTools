# coding: utf-8
"""
@Author : Liuzhenrain
@Create : 16/8/4
"""
import sqlite3
import traceback

dataName = ""
connection = None
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


def SaveToSqlite(databaseName, excel_data_dic={}):
    global dataName
    dataName = databaseName
    conn = _get_connection()
    cursor = conn.cursor()
    # 记录所有的SQL操作语句（增删改），并且将其写入到文件当中
    global sql_command_array
    sql_command_array = []
    for keyName in excel_data_dic.keys():
        # keyname 即为表名

        sqlcommand = "create table `%s` (`rowindex` integer primary key," % keyName
        # 确定EXCEL导入SQL中占用列的个数
        sql_table_ncols = 1  # 所有的表，默认有一个rowindex列

        # 以下数据结构请参照 AnalysisExcel中的_read_excel_data 方法注释
        excel_dic = {}
        excel_dic = excel_data_dic[keyName]
        field_dic = {}
        field_dic = excel_dic["fielddic"]  # field_dic:{fieldname,fieldtype}
        field_name_array = field_dic["fieldname"]
        # 确定表中是否需要unikey
        has_unikey = False
        export_type = field_dic["exporttype"]
        has_unikey, keycount = check_unikey(export_type)
        if has_unikey:
            sqlcommand += " `unikey` text,"
            # 有unikey列，列总数加上一行
            sql_table_ncols += 1
            # has_unikey = True
        sql_table_ncols += len(field_name_array)
        # print sql_table_ncols

        field_name_len = len(field_name_array)
        for i in range(field_name_len):
            field_name = str(field_name_array[i]).lower()
            # if field_name == "index":
            #     field_name = "e_index"
            sqlcommand += ("`" + field_name + "` text")
            if i < field_name_len - 1:
                sqlcommand += ","
        sqlcommand += ");"

        # 首先查询数据库中有没有这个指定的表
        # 下条语句会返回一个sql语句回来，如果能够查询到指定的表名数据
        cursor.execute("select sql from sqlite_master where name='%s' and type='table';" % keyName)
        sql_all = cursor.fetchall()
        if len(sql_all) > 0:
            # print "查询到有%s表" % (keyName)
            # 查询到了指定的表，那就可以开始进行数据比对工作
            # 首先比对列数是否一致。
            cursor.execute("PRAGMA table_info('%s');" % (keyName))
            sql_all = cursor.fetchall()
            if len(sql_all) <> sql_table_ncols:
                # print "数据库表%s的列数和Excel数据应写入的列数%s不一致" % (len(sql_all), sql_table_ncols)
                # 查询出来的列数不一致，先删除表，然后创建表
                try:
                    # 删除表
                    sql_command_array.append("drop table `%s`;" % (keyName))
                    cursor.execute("drop table `%s`;" % (keyName))
                    # 创建表
                    # print "创建表", sqlcommand
                    cursor.execute(sqlcommand)
                    sql_command_array.append(sqlcommand)
                    command_array = get_add_sqlcommand(keyName, excel_dic, has_unikey, keycount)
                    cursor.executescript("".join(command_array))
                    conn.commit()
                except:
                    print traceback.format_exc()
                    conn.rollback()
            else:
                # print "列数一致，进行数据比对"
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
                        conn.rollback()
                else:
                    # print "数据表中有数据", count
                    # 数据表中有数据，对每行数据进行比对，通过rowindex
                    command_array = get_update_command(keyName, excel_dic, has_unikey)
                    if len(command_array) > 0:
                        try:
                            cursor.executescript("".join(command_array))
                            conn.commit()
                        except:
                            print traceback.format_exc()
                            conn.rollback()
                    # 删除在EXCEL中没有但是数据库中有的指定行号的数据
                    command_array = get_delete_command(keyName, excel_dic, has_unikey, keycount)
                    if len(command_array) > 0:
                        try:
                            cursor.executescript("".join(command_array))
                            conn.commit()
                        except:
                            print traceback.format_exc()
                            conn.rollback()
        else:
            # print "没有查询到%s 表" % (keyName)
            # 创建表
            try:
                # print "创建表", sqlcommand
                sql_command_array.append(sqlcommand)
                cursor.execute(sqlcommand)
                conn.commit()
                command_array = get_add_sqlcommand(keyName, excel_dic, has_unikey, keycount)
                cursor.executescript("".join(command_array))
                conn.commit()
            except:
                print traceback.format_exc()
                conn.rollback()
    cursor.close()
    _close_connection()
    return sql_command_array


def get_add_sqlcommand(tablename, excel_data_dic={}, has_unikey=False, keycount=0):
    global sql_command_array
    command_array = []
    # print "开始产生数据库增加语句"
    sqlcommand = "insert into %s (rowindex," % tablename
    field_dic = {}
    field_dic = excel_data_dic["fielddic"]  # field_dic:{fieldname,fieldtype}
    field_name_array = field_dic["fieldname"]
    field_name_len = len(field_name_array)
    for i in range(field_name_len):
        field_name = str(field_name_array[i]).lower()
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
        sql_command_array.append(sqlcommand)
        # 将语句恢复到进入循环之前的状态
        sqlcommand = origin_command
    return command_array


def get_update_command(tablename, excel_data_dic={}, has_unikey=False, keycount =0):
    global sql_command_array
    command_array = []
    data_dic = excel_data_dic["datadic"]
    field_name_array = (excel_data_dic["fielddic"])["fieldname"]
    cursor = _get_connection().cursor()
    origin_command = sql_command = "update `%s` set " % tablename
    for key in data_dic.keys():
        cursor.execute("select * from `%s` where `rowindex` = '%s'" % (tablename, key))
        rowdata = cursor.fetchone()  # 查询到的数据行数据
        # if rowdata == None: # 没有找到对应rowindex的数据
        excel_row_data = data_dic[key]  # excel当中的行数据
        start_index = 1

        excel = ""
        sql = ""
        command = ""

        if has_unikey:
            start_index = 2
            unikeyarray=[]
            for i in range(keycount):
                unikeyarray.append(str(excel_row_data[i]))
            excel = "_".join(unikeyarray)
            sql = rowdata[1]
            if cmp(excel, sql.encode("utf-8")) != 0:
                command += "`unikey`='%s'," % excel
        for index in range(0, len(excel_row_data)):
            excel = excel_row_data[index]
            sql = rowdata[index + start_index]
            if cmp(excel, sql.encode("utf-8")) != 0:
                command += "`%s`='%s'," % (field_name_array[index], excel_row_data[index])
        if len(command) != 0:
            command = command[0:-1]
            sql_command += command
            sql_command += " where `rowindex` = %s;" % key
            command_array.append(sql_command)
            sql_command_array.append(sql_command)
        sql_command = origin_command
    return command_array


def get_delete_command(tablename, excel_data_dic={}, has_unikey=False,keycount =0):
    global sql_command_array
    command_array = []
    origincommand = sqlcommand = "delete from `%s` where `rowindex`=" % tablename
    data_dic = excel_data_dic["datadic"]
    cursor = _get_connection().cursor()
    cursor.execute("select `rowindex` from `%s`;" % tablename)
    for item in cursor:
        rowindex = item[0]
        if not data_dic.has_key(rowindex):
            sqlcommand += "'%s';" % rowindex
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
