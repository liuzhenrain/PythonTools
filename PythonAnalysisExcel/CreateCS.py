# coding: utf-8
"""
Created on 2016/8/13
@author: liuzhenrain
"""
import os


def get_csfile_text(sheet_name, ismain=False, field_dic={}):
    class_name = "Sys%s" % sheet_name
    origin = csText = '''/**\n\
*%s 自动生成，请勿编辑。\n\
*/\n\
\n\
using System;\n\
using System.Collections.Generic;\n\
using System.Text;\n\
\n\
public class %s : SysBase\n\
{\n\
    ///\n\
    ///数据库表名\n\
    ///\n\
    public const string tableName="%s";\n\
''' % (class_name, class_name, sheet_name)
    count = len(field_dic["fieldname"])
    field_name_array = field_dic["fieldname"]
    field_tyep_array = field_dic["fieldtype"]
    field_desc_array = field_dic["fielddesc"]
    field_export_array = field_dic["exporttype"]
    field_text = []
    method_text = []
    for index in range(count):
        field_type = field_tyep_array[index]
        isList = field_type[0] + field_type[-1] == "[]"
        if isList:
            field_type = field_type[1:-1]
        if field_type != 'int' and field_type != 'string' and field_type != 'float':
            field_type = 'Sys%s' % field_type
        if isList:
            text = "    ///\n    ///%s\n    ///\n    public List<%s> %s;" % (
                field_desc_array[index], field_type, field_name_array[index])
        else:
            text = "    ///\n    ///%s\n    ///\n    public %s %s;" % (
                field_desc_array[index], field_type, field_name_array[index])
        field_text.append(text)
    # 开始生成类方法
    method = "    public static %s GetItemByDefault(int pk)\n" % class_name
    method = "%s    {\n" % method
    method = '''%s\t    DataTable table = DataAccess.GetInstance().Query(tableName, "%s", pk);\n\
        if (table.Rows.Count > 0)\n\
        {\n\
            return FromDataRow(table.Rows[0]);\n\
        }\n\
        return null;\n\t}''' % (method, field_name_array[0])
    method_text.append(method)
    csText = "%s\n%s\n%s \n}" % (csText, "\n".join(field_text), "\n".join(method_text))
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
