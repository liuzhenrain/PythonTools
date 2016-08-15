# coding: utf-8
"""
Created on 2016/8/14
@author: liuzhenrain
"""
import os


def get_csfile_text(sheet_name, ismain=False, field_dic={}):
    count = len(field_dic["fieldname"])
    field_name_array = field_dic["fieldname"]
    field_type_array = field_dic["fieldtype"]
    field_desc_array = field_dic["fielddesc"]
    field_export_array = field_dic["exporttype"]
    field_text = []
    method_text = []
    class_name = "Sys%s" % sheet_name
    origin = csText = '''/**\n\
*%s 自动生成，请勿编辑。\n\
*/\n\
\n\
using System.Collections.Generic;\n\
\n\
namespace Philip.Sqlite.DataStruct\n\
{\n\
    public class %s : SysBase\n\
    {\n\
\t    public %s(){\n\
\t\t    base.tableName = tableName;\n\
\t\t    base.defaultcolumn = defaultcolumn;\n\
\t    }
    \t///\n\
    \t/// 数据库表名\n\
    \t///\n\t\
    internal new string tableName="%s";\n\n\
    \t///\n\
    \t/// 默认查询的列名\n\
    \t///\n\t\
    internal new string defaultcolumn="%s";\n\
''' % (class_name, class_name, class_name, sheet_name, field_name_array[0])
    # count = len(field_dic["fieldname"])
    # field_name_array = field_dic["fieldname"]
    # field_type_array = field_dic["fieldtype"]
    # field_desc_array = field_dic["fielddesc"]
    # field_export_array = field_dic["exporttype"]
    # field_text = []
    # method_text = []
    for index in range(count):
        field_type = field_type_array[index]
        isList = field_type[0] + field_type[-1] == "[]"
        if isList:
            field_type = field_type[1:-1]
        if field_type != 'int' and field_type != 'string' and field_type != 'float':
            field_type = 'Sys%s' % field_type
        if isList:
            text = "\t    ///\n\t    /// %s\n\t    ///\n\t    public List<%s> %s;" % (
                field_desc_array[index], field_type, field_name_array[index])
        else:
            text = "\t    ///\n\t    /// %s\n\t    ///\n\t    public %s %s;" % (
                field_desc_array[index], field_type, field_name_array[index])
        field_text.append(text)
    # 开始生成类方法
    # method = "\t    ///\n\t\t/// 获取单条数据\n\t\t///\n"
    # method = "%s\t    internal override SysBase GetItemByDefault(string pk)\n" % method
    # method = "%s\t    {\n" % method
    # method = '''%s\t\t    DataTable table = DataAccess.GetInstance().Query(tableName, "%s", pk);\n\t\
    #     if (table.Rows.Count > 0)\n\t\
    #     {\n\t\
    #         return FromDataRow(table.Rows[0]);\n\t\
    #     }\n\t\
    #     return null;\n\t\t}''' % (method, field_name_array[0])
    # method_text.append(method)
    # method = "\n\t    ///\n\t\t/// 获取多条数据 传入类似:1^2^3^4 的数据\n\t\t///\n"
    # method = "%s\t    internal override List<SysBase> GetListByDefault(string pks)\n" % method
    # method = "%s\t    {\n" % method
    # method = '''%s\t\t    DataTable table = DataAccess.GetInstance().QueryMore(tableName, "%s", pks);\n\t\
    #     return FromDataTable(table);\n\t\t}''' % (method, field_name_array[0])
    # method_text.append(method)
    # method = "\n\t    ///\n\t\t/// 获取多条数据 传入数组[1,2,3,4] 的数据\n\t\t///\n"
    # method = "%s\t    internal override List<SysBase> GetListByDefault(string[] pks)\n" % method
    # method = "%s\t    {\n" % method
    # method = '''%s\t\t    DataTable table = DataAccess.GetInstance().QueryMore(tableName, "%s", string.Join(",", pks));\n\
    #         return FromDataTable(table);\n\t\t}''' % (method, field_name_array[0])
    # method_text.append(method)
    # method = "\n\t    ///\n\t\t/// 读取DataTable数据，返回一个列表\n\t\t///\n"
    # method = "%s\t    private List<SysBase> FromDataTable(DataTable table)\n" % method
    # method = "%s\t    {\n" % method
    # method = '''%s\t\t    List<SysBase> list = new List<SysBase>();\n\t\
    #     foreach (DataRow row in table.Rows)\n\t\
    #     {\n\t\
    #         list.Add(FromDataRow(row));\n\t\
    #     }\n\t\
    #     return list;\n\t\t}''' % method
    # method_text.append(method)
    method = "\n\t    ///\n\t\t/// 读取DataRow数据，返回一个对象\n\t\t///\n"
    method = "%s\t    internal override SysBase FromDataRow(DataRow row)\n" % method
    method = "%s\t    {\n" % method
    method = '''%s\t\t    %s item = new %s();\n''' % (method, class_name, class_name)
    for index in range(count):
        field_type = field_type_array[index]
        field_name = field_name_array[index]
        isList = field_type[0] + field_type[-1] == "[]"
        if isList:
            field_type = field_type[1:-1]
        if field_type != 'int' and field_type != 'string' and field_type != 'float':
            field_type = 'Sys%s' % field_type
        if isList:
            method = '''%s\t\t    item.%s = new List<%s>();\n''' % (method, field_name, field_type)
            if field_type != 'int' and field_type != 'string' and field_type != 'float':
                method = '''%s\t\t    if(!row.IsNullOrEmpty("%s"))\n\t\t\t{\n\t\
            item.%s.AddRange(DataAccess.GetList<%s>(row.GetString("%s")));\n\t\t\t}\n''' % (
                    method, field_name, field_name, field_type, field_name)
            elif field_type == 'int':
                method = '''%s\t\t    item.%s.AddRange(row.GetInt32s("%s"));\n''' % (
                    method, field_name, field_name)
            elif field_type == 'string':
                method = '''%s\t\t    item.%s.AddRange(row.GetStrings("%s"));\n''' % (
                    method, field_name, field_name)
            elif field_type == 'float':
                method = '''%s\t\t    item.%s.AddRange(row.GetFloats("%s"));\n''' % (
                    method, field_name, field_name)
        else:
            if field_type != 'int' and field_type != 'string' and field_type != 'float':
                method = '''%s\t\t    item.%s = DataAccess.GetItem<%s>(row.GetString("%s"));\n''' % (
                    method, field_name, field_type, field_name)
            elif field_type == 'int':
                method = '''%s\t\t    item.%s = row.GetInt32("%s");\n''' % (
                    method, field_name, field_name)
            elif field_type == 'string':
                method = '''%s\t\t    item.%s = row.GetString("%s");\n''' % (
                    method, field_name, field_name)
            elif field_type == 'float':
                method = '''%s\t\t    item.%s = row.GetFloat("%s");\n''' % (
                    method, field_name, field_name)
    method = "%s\t\t    return item;\n\t\t}" % method
    method_text.append(method)
    csText = "%s\n%s\n\n%s \n\t}\n}" % (csText, "\n".join(field_text), "\n".join(method_text))
    return csText


def create_csfile(path, sheet_data_dic):
    # 判定是否存在指定路径的文件夹
    if not os.path.isdir(path):
        # 创建指定路径的文件夹
        os.mkdir(path)
    for sheet_name in sheet_data_dic.keys():
        sheet_dic = sheet_data_dic[sheet_name]
        field_dic = sheet_dic["fielddic"]
        ismain = sheet_dic["ismain"]
        csText = get_csfile_text(sheet_name, ismain, field_dic)
        csfile = open("%s%s%s.cs" % (path, os.sep, "Sys" + sheet_name), "w")
        csfile.write(csText)
        csfile.close()
