#导出Excel数据到Sqlite3中
- 确定excelfile文件夹和ExcelToSqlite.py在同一级目录下
- 参照excelfile文件夹下excel文件的格式。
    请参照如下格式
    
    | 说明     | 说明        | 说明     | 说明 |
    | ------- | ------------- | --------- |-----|
    | 导出类型 | 导出类型 | 导出类型 | 导出类型 |
    | 数据类型    | 数据类型        | 数据类型     | 数据类型 |
    | 列名    | 列名        | 列名     | 列名 |
    | 数据    | 数据        | 数据     | 数据      |
    
## Python相关
    1. import traceback    print traceback.format_exc() 显示详细的错误信息
    
## Sqlite3相关
    1. cursor.execute("PRAGMA table_info('%s');" % (keyName)) 可以查询制定表的相关信息包括所有的字段名，字段类型
    
        | cid | name | type | notnull | dflt_value | pk |
        | --- | --- | --- | --- | --- | --- |
        |具体的数据|具体的数据|具体的数据|具体的数据|具体的数据|具体的数据|