# coding: utf-8
"""
@Author : Liuzhenrain
@Create : 16/8/4
"""
import sqlite3

dataName =""
connection = None

def SaveToSqlite(data, excel_data_dic = {}):
    global dataName
    dataName = data
    for keyName in excel_data_dic.keys():
        conn = _get_connection()

        print keyName


def _get_connection():
    global connection
    connection = sqlite3.connect(dataName)
    return connection


def _close_connection():
    global connection
    if connection <> None:
        connection.close()
