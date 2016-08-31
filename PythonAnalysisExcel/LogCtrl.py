# coding: utf-8
"""
@Author : Liuzhenrain
@Create : 16/8/9
"""

logMsg = []


def log(msg):
    global logMsg
    print msg
    logMsg.append(msg)


def write_log_file():
    logfile = open("log.log", "w");
    logfile.write("\n".join(logMsg));
    logfile.close()
