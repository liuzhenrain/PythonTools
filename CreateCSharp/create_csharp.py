import typing
from random_word import RandomWords
import string
import os
import random
from csharp_type import AccessType, ObjectType, CSharpClass, CSharpFunc, CSharpProp

add_printTool = 0
random_word = RandomWords()
csharp_class_list = []  # type: List[CSharpClass]


def get_random_word(fUpper=True):
    _text = random_word.get_random_word(hasDictionaryDef='true').replace('-', '')
    if fUpper:
        return _text.title()
    else:
        return _text


def get_suojin(count=1):
    return "\t" * count


def create_props(c_class: CSharpClass):
    prop_item = CSharpProp()
    prop_item.name = get_random_word()
    prop_item.accessType = AccessType[random.randint(0, len(AccessType) - 1)]
    prop_item.objType = ObjectType[random.randint(0, len(ObjectType) - 1)]
    prop_item.isStatic = True if random.randint(0, 1) == 1 else False
    prop_item.text = "\n\t%s%s %s %s;" % (prop_item.accessType, " static" if prop_item.isStatic else '',
                                          prop_item.objType, prop_item.name)
    return prop_item


def create_class(class_name: str, addDebug: bool):
    print("Create Class Name:", class_name)
    csharp_class = CSharpClass(class_name)
    prop_count = random.randint(5, 10)
    for index in range(prop_count):
        prop = create_props(csharp_class)
        csharp_class.add_prop(prop)
        if prop.isStatic :
            csharp_class.hasStaticProp = True
        if prop.accessType != "private":
            csharp_class.hasPublic = True
    func_count = random.randint(1, 10)
    for index in range(func_count):
        func = create_func(csharp_class)
        csharp_class.add_func(func)


def create_if_block(pType: str, pName: str, pValue: str,isStaticFunc:bool,cClass:CSharpClass):
    pBody = [get_suojin(3) + "int %s = %d;" % (get_random_word(False), random.randint(10, 10000))]
    c_class_2 = CSharpClass("")
    if len(csharp_class_list)<=2 :
        pBody.append("\n")
    elif csharp_class_list.__len__() > 2:
        cClassIndex = csharp_class_list.index(cClass)
        class2Index = 0
        while True:
            class2Index = random.randint(0,len(csharp_class_list)-1)
            if class2Index != cClassIndex:
                break
        c_class_2 = csharp_class_list[class2Index]
        if isStaticFunc and cClass.hasStaticProp == False :
            pBody.append(get_suojin(3) + "string %s = %s;" % (get_random_word(False), get_random_word(False)))
        else:
            _prop_array_1 = cClass.propArray  # type:list[CSharpProp]
            _prop_array_2 = c_class_2.propArray  # type:list[CSharpProp]
            _prop_1 = None
            if isStaticFunc :
                for item in cClass.propArray:
                    if item.isStatic == isStaticFunc :
                        _prop_1 = item
                        break
            else:
                _prop_1 = _prop_array_1[random.randint(0,len(_prop_array_1)-1)]
            ## 此处逻辑需要找到第二个类的一个属性，保证可访问属性就行了，然后需要改写下面的字符串内容
            _prop_2 = None
            if not c_class_2.hasPublic :
                pBody.append(get_suojin(3) + "string %s = %s;" % (get_random_word(False), get_random_word(False)))
            else:
                for item in _prop_array_2:
                    if item.objType == _prop_1.objType and item.accessType != "private" :
                        _prop_2 = item
                        break
                if _prop_2 != None :
                    _temp = get_suojin(3) + "%s%s = %s%s;" % (cClass.name+"." if _prop_1.isStatic else "",
                                                            _prop_1.name,
                                                            c_class_2.name+"." if _prop_2.isStatic else c_class_2.name+".Instance.",
                                                            _prop_2.name)
                    pBody.append(_temp)
    _text = get_suojin(2) + "if(%s != %s){\n%s\n%s}" % (pName, pValue, "\n".join(pBody), get_suojin(2))
    return _text

def create_func_body(c_class: CSharpClass, p_dic, func_is_static=False):
    _block_count = random.randint(1, 10)
    text = []
    for index in range(_block_count):
        objType = ObjectType[random.randint(0,len(ObjectType)-1)]
        pName = get_random_word(False)
        _temp = get_suojin(2) + "%s %s = %s;"
        if objType == "int" :
            _temp_value = random.randint(100,59878)
        elif objType == "string" :
            _temp_value = ",".join(random_word.get_random_words(limit=10))
        elif objType == "float" :
            _temp_value = random.uniform(10.12,876348.18)
        elif objType == "GameObject":
            _temp_value = "new GameObject(\"%s\")" % (pName)
        elif objType == "Text":
            _temp_value = "new Text()"


def create_func(c_class):
    func_item = CSharpFunc()
    func_item.name = get_random_word()
    func_item.isStatic = False if random.randint(0, 1) == 0 else True
    func_item.accessType = AccessType[random.randint(0, len(AccessType) - 1)]
    func_item.hasReturn = False if random.randint(0, 1) == 0 else True
    func_item.returnType = ObjectType[random.randint(0, len(ObjectType) - 1)] if func_item.hasReturn else "void"
    _param_count = random.randint(0, 5)
    _param_text = ""
    _param_dict = {}
    if _param_count > 0:
        for i in range(_param_count):
            _pType = AccessType[random.randint(0, len(AccessType) - 1)]
            _pName = get_random_word(False)
            if _pName in _param_dict:
                _pName = _pName + str(i)
            _param_dict[_pName] = _pType
            _param_text = _param_text + ("%s %s %s" % (_pType, _pName, "," if i < _param_count - 1 else ""))

    func_item.text = "\n\t%s%s %s %s(%s){\n\t\t%s\n\t}" % (func_item.accessType,
                                                           " static" if func_item.isStatic else "",
                                                           func_item.returnType,
                                                           func_item.name,
                                                           _param_text,
                                                           create_func_body(c_class, _param_dict, func_item.isStatic))
    return func_item


def createFiles(count, addPrintTool:bool):
    class_name_array = random_word.get_random_words(
        limit=count * 2, hasDictionaryDef='true')
    for index in range(count):
        class_name = "%s%s" % (str(class_name_array[index]).title().replace(
            '-', ''), str(class_name_array[index + count]).title().replace('-', ''))
        create_class(class_name, add_printTool)


if __name__ == "__main__":
    class_count = input("确定你需要创建的类的数量:")
    printLog = input("是否加入 PrintTool.Log() 函数 (输入 1/0 ):")
    add_printTool = True if printLog == "1" else False
    createFiles(int(class_count), add_printTool)
    # print(random_word.get_random_words(limit=10))
