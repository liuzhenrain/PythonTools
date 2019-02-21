AccessType = ["public", "protected", "internal", "private"]
ObjectType = ["int", "string", "bool", "float", "GameObject", "Text"]


class CSharpClass:
    def __init__(self, class_name, superClass=""):
        self.name = class_name
        self.accessType = 0
        self.isBase = False
        self.inheritMono = False
        self.superClass = superClass
        self.funcArray = []
        self.propArray = []
        self.refCount = 0
        self.hasStaticProp = False
        self.hasPublic = False

    def add_func(self, csharp_func):
        self.funcArray.append(csharp_func)

    def add_prop(self, parameter):
        self.propArray.append(parameter)


class CSharpFunc:
    def __init__(self):
        self.accessType = 0
        self.name = ""
        self.isStatic = False
        self.text = ""
        self.hasReturn = False
        self.returnType = ""


class CSharpProp:
    def __init__(self):
        self.accessType = ""
        self.name = ""
        self.objType = ""
        self.isStatic = False
        self.text = ""
