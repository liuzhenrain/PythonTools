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
    2. f=open('f.txt','w')    # r只读，w可写，a追加
    3. ticks = time.time()  获取当前时间的时间戳,是一个浮点型数据 例如当前时间 :2016-08-10 00:16 后面省略 时间戳为:1470759447.779779
        localt = time.localtime(ticks)
            返回:time.struct_time(tm_year=2016, tm_mon=8, tm_mday=10, tm_hour=0, tm_min=18, tm_sec=41, tm_wday=2, tm_yday=223, tm_isdst=0)
            可以使用 localt.tm_year 获取对应的数据 2016
    
## Sqlite3相关
    1. cursor.execute("PRAGMA table_info('%s');" % (keyName)) 可以查询制定表的相关信息包括所有的字段名，字段类型
    
        | cid | name | type | notnull | dflt_value | pk |
        | --- | --- | --- | --- | --- | --- |
        |具体的数据|具体的数据|具体的数据|具体的数据|具体的数据|具体的数据|