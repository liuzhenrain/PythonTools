#!/usr/bin/env python
# coding: utf-8
"""
Created on 2016/9/8
@author: liuzhenrain
"""

import os
from ExcelToSqlite import savetosqlite

if __name__ == "__main__":
    pathFolder = os.path.abspath('.') + os.sep + "excelfile"
    savetosqlite(pathFolder, [{"name": "achieve.xls"}], False)
