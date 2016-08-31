#!/usr/bin/env python
# coding: utf-8
"""
创建命令行脚本，并且打包成gz文件
Created on 2016/8/25
@author: liuzhenrain
"""
import gzip
import os
import time

BufSize = 1024 * 8


def create_command_file(has_db, sqlcommands=[]):
    if not has_db:
        return
    global BufSize
    gz = GZipTool(BufSize)
    ticks = int(time.time())
    localtime = time.localtime(ticks)
    timestr = "-".join([str(localtime.tm_year), str(localtime.tm_mon), str(localtime.tm_mday)])

    if not os.path.exists("commandFiles"):
        print u"已经有了command文件了"
        os.mkdir("commandFiles")

    gzfile_path = "commandFiles/commandFile(%s).gz" % ticks
    txtfile_path = "commandFiles/commandFile(%s).txt" % ticks

    if not os.path.exists(gzfile_path):
        file_list = open("commandFiles/filelist.txt", "a")
        file_list.write("commandFile(%s).gz\n" % ticks)
        file_list.close()
    else:
        gz.decompress(gzfile_path, txtfile_path)
        os.remove(gzfile_path)
    txtfile = open(txtfile_path, "a")
    txtfile.write("\n".join(sqlcommands))
    txtfile.write("\n")
    txtfile.close()
    gz.compress(txtfile_path, gzfile_path)
    os.remove(txtfile_path)


class GZipTool:
    def __init__(self, bufSize):
        self.bufSize = bufSize
        self.fin = None
        self.fout = None

    def compress(self, src, dst):
        self.fin = open(src, 'rb')
        self.fout = gzip.open(dst, 'wb')

        self.__in2out()

    def decompress(self, gzFile, dst):
        self.fin = gzip.open(gzFile, 'rb')
        self.fout = open(dst, 'wb')

        self.__in2out()

    def __in2out(self, ):
        while True:
            buf = self.fin.read(self.bufSize)
            if len(buf) < 1:
                break
            self.fout.write(buf)

        self.fin.close()
        self.fout.close()
