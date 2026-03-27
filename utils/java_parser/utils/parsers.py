import re
import sys
from typing import List

sys.path.extend([".", ".."])
import pickle
from loguru import logger
from tree_sitter import Parser
from Config import JAVA_LANGUAGE, KNOWN_ASSERTIONS
from entities.Class import Class, Interface
from entities.Method import Method, MethodInvocation, Constructor
from entities.Variable import Variable, Field, Parameter, Type


def parse_variables(method_node):
    """
    This function is used to parse the variables from a given method node.
    It uses the tree-sitter query language to extract the variables and their attributes.

    Args:
        method_node (tree_sitter.Node): The method node to parse variables from.

    Returns:
        list: A list of Variable objects, each representing a variable in the method.
    """

    ret = []
    # Query to capture the local variable declarations in the method body
    variable_query = JAVA_LANGUAGE.query("(local_variable_declaration) @var")

    # Query to capture the type and name of the local variable
    variable_attr_query = JAVA_LANGUAGE.query(
        """
        (local_variable_declaration[
            type: (_) @type 
            declarator: (_ [
                name: (identifier) @name 
            ])
        ])
        """
    )

    # Execute the variable query on the method node
    variables = variable_query.captures(method_node).get('var', [])

    # For each variable captured
    for variable in variables:
        # Execute the attribute query on the variable node
        attrs = variable_attr_query.captures(variable)

        names = sorted(attrs.get('name', []), key=lambda x: x.start_byte)
        names = [name for name in names if
                 name.parent.parent == variable]  # Ensure names are direct children of the variable node
        types = sorted(attrs.get('type', []), key=lambda x: x.start_byte)
        types = [type_ for type_ in types if
                 type_.parent == variable]  # Ensure types are direct children of the variable node

        if len(names) == 0 or len(types) == 0:
            logger.error(
                f"Variable Declaration {str(variable[0].text, encoding='utf-8')} has no name or type.")
            continue

        # Ensure that there are exactly two attributes (type and name)
        if len(names) > 1:
            if len(types) == 1:
                types = [types[0]] * len(names)  # Extend the type to match the number of names
                pass
            else:
                logger.error(f"Unknown Error of Variable Declaration Node. Please check.")

                exit(-1)

        assert len(names) == len(types), \
            f"Variable Declaration {str(variable[0].text, encoding='utf-8')} has different number of names and types."

        for _type, _name in zip(types, names):
            v = Variable()  # Create a new Variable object
            v._name = str(_name.text, encoding='utf-8')
            v._type = Type.build_type(str(_type.text, encoding='utf-8'))
            # Ensure that the Variable object has both a name and a type
            assert str(v.type) != '' and v.name != '', \
                f"Variable Declaration {str(variable[0].text, encoding='utf-8')} has no name or type."
            # Add the Variable object to the return list
            ret.append(v)

    # Return the list of Variable objects
    return ret


def parse_callees(method_node):
    """
        This function is used to parse the method invocations (callees) from a given method node.
        It uses the tree-sitter query language to extract the callees and their attributes.

        Args:
            method_node (tree_sitter.Node): The method node to parse callees from.

        Returns:
            list: A list of MethodInvocation objects, each representing a method invocation in the method.
        """
    ret = []
    record = set()
    callee_detail_query = JAVA_LANGUAGE.query("""
    (method_invocation[
        object: (_) @object
        name: (_) @name
        arguments: (argument_list)@arg_list
    ])
    """)
    callee_query = JAVA_LANGUAGE.query("(method_invocation) @callee")
    callees = callee_query.captures(method_node).get('callee', [])
    for callee in callees:
        if any([assert_method in str(callee.text, encoding='utf-8') for assert_method in
                KNOWN_ASSERTIONS]):
            # 去除assertion的调用
            continue
        invocation_str = str(callee.text, encoding='utf-8')
        mi = MethodInvocation()
        obj_node = callee.child_by_field_name('object')
        name_node = callee.child_by_field_name('name')
        args_node = callee.child_by_field_name('arguments')
        if obj_node:
            mi._object = str(obj_node.text, encoding='utf-8')
            pass
        if name_node:
            mi._method_name = str(name_node.text, encoding='utf-8')
        else:
            logger.error(f"Method invocation {invocation_str} has no method name.")
        if args_node:
            args = [
                str(node.text, encoding='utf-8')
                for node in args_node.children[1:-1]
                if getattr(node, 'type', None) != ','
            ]
            mi._param_list = args
        else:
            logger.warning(f"Method invocation {invocation_str} has no argument lists.")
        ret.append(pickle.loads(pickle.dumps(mi)))
    return ret


def parse_constructor(class_str: str):
    parser = Parser()
    parser.language = JAVA_LANGUAGE
    tmp_class_str = pickle.loads(pickle.dumps(class_str))
    tree = parser.parse(bytes(tmp_class_str, "utf-8"))

    method_query = JAVA_LANGUAGE.query(
        """
        (constructor_declaration) @method_decl
        """
    )

    constructor_attr_query = JAVA_LANGUAGE.query(
        """
        (constructor_declaration
            (modifiers) @modifier
            name: (_) @name
            (formal_parameters) @params
            body: (_) @body
        )
        """
    )

    rets = []
    methods = method_query.captures(tree.root_node).get('method_decl', [])
    for method_node in methods:
        m = Constructor()
        m._param_list = []
        m._local_variables = parse_variables(method_node)
        m._callees = parse_callees(method_node)
        m._method_body = str(method_node.text, encoding='utf-8')
        attrs = constructor_attr_query.captures(method_node)
        name_list = sorted(attrs.get('name', []), key=lambda x: x.start_byte)
        modifier_list = sorted(attrs.get('modifier', []), key=lambda x: x.start_byte)
        body_list = sorted(attrs.get('body', []), key=lambda x: x.start_byte)
        params_list = sorted(attrs.get('params', []), key=lambda x: x.start_byte)

        if len(name_list) != len(modifier_list) or len(name_list) != len(body_list) or len(name_list) != len(
                params_list):
            logger.warning(
                f"Attribute count of Constructor Declaration {str(method_node.text, encoding='utf-8')} mismatch"
            )
            continue

        for modifier, name, body, params in zip(modifier_list, name_list, body_list, params_list):
            m._modifiers = str(modifier.text, encoding='utf-8').split()
            m._method_name = str(name.text, encoding='utf-8')
            # m._method_body = str(body.text, encoding='utf-8')
            for tmp_node in params.children:
                if tmp_node.type == 'formal_parameter':
                    p = Parameter()
                    if tmp_node.children[0].type == 'modifiers':
                        p._modifiers = [str(tmp_node.children[0].text, encoding='utf-8')]
                        assert 'type' in tmp_node.children[1].type
                        assert tmp_node.children[2].type == 'identifier'
                        p._type = Type.build_type(tmp_node.children[1].text.decode('utf-8'))
                        p._name = tmp_node.children[2].text.decode('utf-8')
                    else:
                        assert 'type' in tmp_node.children[0].type
                        assert tmp_node.children[1].type == 'identifier'
                        p._type = Type.build_type(tmp_node.children[0].text.decode('utf-8'))
                        p._name = tmp_node.children[1].text.decode('utf-8')
                    m._param_list.append(p)

        param_strings = [str(obj) for obj in m._param_list]
        m._method_signature = str(method_node.text, encoding='utf-8').split('{')[0]
        # m._method_signature = str(m._return_type) + ' ' + m._method_name + '(' + ', '.join(param_strings) + ')'
        rets.append(pickle.loads(pickle.dumps(m)))
    return rets


def parse_methods(class_str: str):
    """
    This function is used to parse the methods from a given class string.
    It uses the tree-sitter query language to extract the methods and their attributes.

    Args:
        class_str (str): The class string to parse methods from.

    Returns:
        list: A list of Method objects, each representing a method in the class.
    """
    parser = Parser()
    parser.language = JAVA_LANGUAGE
    tmp_class_str = pickle.loads(pickle.dumps(class_str))
    tree = parser.parse(bytes(tmp_class_str, "utf-8"))

    rets = []

    # 查询所有方法声明节点
    method_query = JAVA_LANGUAGE.query(
        """
        (method_declaration) @method_decl
        """
    )

    # 提取方法属性：修饰符、返回类型、名称、参数、体
    method_attr_query = JAVA_LANGUAGE.query(
        """
        (method_declaration
            type: (_) @ret_type
            name: (_) @name
            (formal_parameters) @params
            body: (_)? @body
        )
        """
    )

    methods = method_query.captures(tree.root_node).get('method_decl', [])

    for method_node in methods:
        m = Method()
        m._param_list = []
        m._local_variables = parse_variables(method_node)
        m._callees = parse_callees(method_node)
        m._method_body = str(method_node.text, encoding='utf-8')

        # 获取并排序各属性
        attrs = method_attr_query.captures(method_node)

        # modifier_list = sorted(attrs.get('modifier', []), key=lambda x: x.start_byte)
        return_type_list = sorted(attrs.get('ret_type', []), key=lambda x: x.start_byte)
        name_list = sorted(attrs.get('name', []), key=lambda x: x.start_byte)
        params_list = sorted(attrs.get('params', []), key=lambda x: x.start_byte)
        body_list = sorted(attrs.get('body', []), key=lambda x: x.start_byte)

        # 检查属性数量是否一致
        if len(name_list) != len(return_type_list) or \
                len(name_list) != len(params_list):
            logger.warning(
                f"Attribute count of Method Declaration {str(method_node.text, encoding='utf-8')} mismatch, "
            )
            continue

        # 取第一个结果即可（每个方法只有一个）
        modifier = None
        for child in method_node.children:
            if child.type == 'modifiers':
                modifier = child.text.decode()
                break
        if modifier is None:
            modifier = 'private'
        return_type = return_type_list[0]
        name = name_list[0]
        params = params_list[0]
        body = body_list[0] if body_list else None

        # 设置基本属性
        m._modifiers = modifier
        m._return_type = Type.build_type(str(return_type.text, encoding='utf-8'), method_node=method_node)
        m._method_name = str(name.text, encoding='utf-8')
        # if body:
        #     m._method_body = str(body.text, encoding='utf-8')

        # 解析参数列表
        for tmp_node in params.children:
            if tmp_node.type == 'formal_parameter':
                p = Parameter()
                for child in tmp_node.children:
                    if child.type == 'modifiers':
                        p._modifiers.append(child.text.decode('utf-8'))
                    elif 'type' in child.type:
                        p._type = Type.build_type(child.text.decode('utf-8'))
                    elif child.type == 'identifier':
                        p._name = child.text.decode('utf-8')
                m._param_list.append(p)

        # 构造方法签名
        param_strings = [str(obj) for obj in m._param_list]
        m._method_signature = str(method_node.text, encoding='utf-8').split('{')[0]
        # m._method_signature = f"{m._return_type} {m._method_name}({', '.join(param_strings)})"

        # 判断是否是测试方法
        for modi in m._modifiers:
            if modi.startswith('@Test'):
                m._is_test_method = True
                break

        rets.append(pickle.loads(pickle.dumps(m)))

    # 最后添加构造函数
    rets.extend(parse_constructor(class_str))

    return rets


def has_one_class(class_str):
    """
    判断一个给定的代码文件中是否只包含一个类

    Args:
        class_str (str): 给定的代码文件内容

    Returns:
        boolean: 是否只包含一个类
    """
    parser = Parser()
    parser.language = JAVA_LANGUAGE
    tree = parser.parse(bytes(class_str, "utf-8"))
    class_decl_query = JAVA_LANGUAGE.query(
        """
        (class_declaration) @class_decl
        """)
    res = class_decl_query.captures(tree.root_node).get('class_decl', [])
    # 如果查询结果的长度为1，说明只包含一个类
    if len(res) == 1:
        return True
    else:
        return False
    pass


def parse_class_declaration(class_str: str, file: str):
    """
    This function is used to parse the class declaration from a given class string.
    It uses the tree-sitter query language to extract the class and its attributes.

    Args:
        class_str (str): The class string to parse class declaration from.

    Returns:
        list: A list of Class objects, each representing a class in the class string.
    """
    parser = Parser()
    parser.language = JAVA_LANGUAGE
    tree = parser.parse(bytes(class_str, "utf-8"))

    # 提取导入语句
    imports = parse_import_stmts(class_str)

    # 查询所有类声明节点
    class_query = JAVA_LANGUAGE.query("(class_declaration) @class_decl")
    class_nodes = class_query.captures(tree.root_node).get("class_decl", [])

    all_cls_objs = []

    # 提取 package 声明
    package_query = JAVA_LANGUAGE.query("(package_declaration) @package")
    package_captures = package_query.captures(tree.root_node).get("package", [])

    pkg_name = None
    if len(package_captures) > 0:
        # assert len(package_captures) == 1
        package_text = str(package_captures[0].text, encoding='utf-8')
        parts = package_text.split()
        if len(parts) >= 2 and parts[0] == 'package':
            pkg_name = parts[1].strip().rstrip(';').strip()

    for class_node in class_nodes:
        cls_node = class_node  # 获取 Node 对象
        cls_obj = _parse_class_obj(cls_node, file)

        # 设置类的全局属性
        cls_obj._imports = [i for i in imports]  # 可选：深拷贝或直接赋值
        cls_obj._package = pkg_name or ''
        cls_obj._class_signature = f"{pkg_name}.{cls_obj.name}" if pkg_name else cls_obj.name

        # 将类签名传递给每个方法
        for method in cls_obj._class_methods:
            method._belongs = cls_obj.signature

        all_cls_objs.append(cls_obj)

    return all_cls_objs


def _parse_class_obj(cls_decl_node, file):
    cls_obj = Class()
    cls_obj._file_path = file
    if cls_decl_node.children[0].type == 'modifiers':
        cls_obj._modifiers = str(cls_decl_node.children[0].text, encoding='utf-8').split()
        pass
    else:
        cls_obj._modifiers = ['private']
    name_node = cls_decl_node.child_by_field_name('name')
    cls_name = str(name_node.text, encoding='utf-8')
    cls_obj._class_name = cls_name
    cls_body_start = cls_decl_node.child_by_field_name('body').byte_range[0]
    cls_decl_start = cls_decl_node.byte_range[0]
    cls_declaration_text = str(cls_decl_node.text[:cls_body_start - cls_decl_start],
                               encoding='utf-8').strip()
    cls_obj._declaration = cls_declaration_text
    cls_obj._text = str(cls_decl_node.text, encoding='utf-8')
    cls_obj._class_methods = parse_methods(cls_obj._text)
    cls_obj._class_fields = parse_fields(cls_obj._text)
    if 'abstract' in cls_obj.modifiers:
        cls_obj._is_abstract = True

    if is_test_class(cls_decl_node.text.decode('utf-8')):
        text = cls_decl_node.text.decode('utf-8')
        for m in cls_obj._class_methods:
            if m.is_test:
                text = text.replace(m._text, '')
        cls_obj._test_class_setup = text
        cls_obj._is_test_class = True

    return cls_obj


def _parse_interface_obj(cls_decl_node):
    interface_obj = Interface()
    if cls_decl_node.children[0].type == 'modifiers':
        interface_obj._modifiers = str(cls_decl_node.children[0].text, encoding='utf-8').split()
        pass
    else:
        interface_obj._modifiers = ['private']
    name_node = cls_decl_node.child_by_field_name('name')
    cls_name = str(name_node.text, encoding='utf-8')
    interface_obj._class_name = cls_name
    interface_body_start = cls_decl_node.child_by_field_name('body').byte_range[0]
    interface_decl_start = cls_decl_node.byte_range[0]
    interface_declaration_text = str(cls_decl_node.text[:interface_body_start - interface_decl_start],
                                     encoding='utf-8').strip()
    interface_obj._declaration = interface_declaration_text
    interface_obj._text = str(cls_decl_node.text, encoding='utf-8')
    interface_obj._class_methods = parse_methods(interface_obj._text)
    interface_obj._class_fields = parse_fields(interface_obj._text)
    if 'abstract' in interface_obj.modifiers:
        interface_obj._is_abstract = True

    if is_test_class(cls_decl_node.text.decode('utf-8')):
        text = cls_decl_node.text.decode('utf-8')
        for m in interface_obj._class_methods:
            if m.is_test:
                text = text.replace(m._text, '')
        interface_obj._test_class_setup = text
        interface_obj._is_test_class = True

    return interface_obj


def is_test_class(java_code):
    # Check if class name contains 'Test'
    class_name_pattern = re.compile(r'class\s+(\w*Test\w*)\s*{')
    class_name_match = class_name_pattern.search(java_code)
    if class_name_match:
        return True

    # Check for test annotations (JUnit)
    junit_annotation_pattern = re.compile(r'@\s*Test')
    if junit_annotation_pattern.search(java_code):
        return True

    # Check for test framework imports (JUnit, TestNG)
    test_framework_imports = [
        'org.junit.Test',
        'org.junit.jupiter.api.Test',
        'org.testng.annotations.Test'
    ]
    for import_statement in test_framework_imports:
        if import_statement in java_code:
            return True

    return False


def parse_import_stmts(file_code: str):
    """
    从给定的代码文件内容中提取import。为了避免噪音，需要满足两个条件：
    1. import语句必须是分号结尾
    2. import语句至多含有三个以空格区分的token

    Args:
        file_code (str): 输入的代码文件内容（最好是代码文件，其他文件中可能会被过滤掉）

    Returns:
        list: 从输入内容中提取出的import strings
    """
    rets = []
    parser = Parser()
    parser.language = JAVA_LANGUAGE
    tree = parser.parse(bytes(file_code, "utf-8"))
    import_decl_query = JAVA_LANGUAGE.query(
        """
    (import_declaration) @import_decl
    """
    )
    imports = import_decl_query.captures(tree.root_node).get('import_decl', [])
    for import_stmt in imports:
        import_stmt = str(import_stmt.text, encoding="utf-8")
        tks = import_stmt.split()
        if import_stmt.endswith(";") and (len(tks) == 2 or len(tks) == 3):
            rets.append(import_stmt)
    return rets


def parse_fields(class_str: str) -> List[Field]:
    """
    Analyze defined fields for given class.
    :param class_str: class code in a string.
    :return: list of Field
    """
    java_modifiers = [
        "public",
        "protected",
        "private",
        "static",
        "final",
        "abstract",
        "synchronized",
        "volatile",
        "transient",
        "native",
        "default"
    ]

    parser = Parser()
    parser.language = JAVA_LANGUAGE
    tree = parser.parse(bytes(class_str, "utf-8"))
    rets = []
    field_decl_query = JAVA_LANGUAGE.query("""(field_declaration) @field_decl""")
    field_attr_query = JAVA_LANGUAGE.query(
        """
        (field_declaration
            type: (_) @type_name
            declarator: (variable_declarator name: (identifier)@var_name)
        ) 
        """
    )

    fields = field_decl_query.captures(tree.root_node).get('field_decl', [])
    for field_decl in fields:
        # Get attributes of the field declaration
        attrs = field_attr_query.captures(field_decl)

        # Sort attributes by their start byte position
        type_name_list = sorted(attrs.get('type_name', []), key=lambda x: x.start_byte)
        type_name_list = [type_name for type_name in type_name_list if type_name.parent == field_decl]
        var_name_list = sorted(attrs.get('var_name', []), key=lambda x: x.start_byte)
        var_name_list = [var_name for var_name in var_name_list if var_name.parent.parent == field_decl]

        if len(type_name_list) != 1:
            logger.error('Field Declaration has no type name or multiple type names.')

        type_name_list = [type_name_list[0]] * len(var_name_list)  # Extend type names to match variable names

        for type_name, var_name in zip(type_name_list, var_name_list):
            field_obj = Field()
            field_obj._type = Type.build_type(str(type_name.text, encoding="utf-8"))
            field_obj._name = str(var_name.text, encoding="utf-8")
            field_obj._declaration = str(field_decl.text, encoding="utf-8")

            # Extract modifiers
            tokens = field_obj._declaration.split(' ')
            for token in tokens:
                if token in java_modifiers:
                    field_obj._modifiers.append(token)

            # Extract initial value if exists
            value = ''
            if '=' in field_obj._declaration:
                value = field_obj._declaration.split('=')[1].strip().strip(';')
            field_obj._init_value = value

            if (field_obj._name != ""
                    and field_obj._modifiers != ""
                    and field_obj._type is not None
                    and field_obj._declaration != ""
            ):
                rets.append(field_obj)

    return rets


# Unused for now.......

def has_branch(focal_method):
    """
    判断一个给定的函数里是否包含分支，用于计算分支覆盖率

    Args:
        focal_method (_type_): 给定的函数

    Returns:
        boolean: 是否包含分支
    """
    parser = Parser()
    parser.language = JAVA_LANGUAGE
    focal_method = "public class TmpClass {\n" + focal_method + "\n}"
    tree = parser.parse(bytes(focal_method, "utf8"))
    query = JAVA_LANGUAGE.query(
        """
        (if_statement )@if
        (for_statement )@for
        (while_statement) @while
        (catch_clause) @catch
        (switch_expression) @sw
        """
    )

    res = [item for branches in query.captures(tree.root_node).values() for item in branches]
    if len(res) != 0:
        return True
    else:
        return False


def _filter_attributes(subjects, targets):
    if len(subjects) % len(targets) == 0:
        return True, subjects
    if len(subjects) < len(targets):
        return False, []
    matched_index = 0
    for idx, subject in enumerate(subjects):
        if subject[1] == targets[idx % (len(targets))]:
            if idx != 0 and (idx + 1) % len(targets) == 0:
                matched_index = idx
            else:
                continue
        else:
            return False, subjects[:matched_index + 1]


def parse_superclass_or_interface_from_class_node(class_str: str):
    parser = Parser()
    parser.language = JAVA_LANGUAGE
    super_class_query = JAVA_LANGUAGE.query("(class_declaration superclass: (_) @supc)")
    tree = parser.parse(bytes(class_str, "utf-8"))
    superclasses = super_class_query.captures(tree.root_node).get('supc', [])
    superclasses = [str(sc.text, encoding='utf-8') for sc in superclasses]
    interfaces_query = JAVA_LANGUAGE.query("(class_declaration interfaces: (_) @intf)")
    interfaces = interfaces_query.captures(tree.root_node).get('intf', [])
    interfaces = [str(sc.text, encoding='utf-8') for sc in interfaces]

    return {
        "superclasses": superclasses,
        "interfaces": interfaces
    }


# TODO

def parse_classes_from_file_node(file_code: str, strategy="generation"):
    """
    处理一下生成的代码中的inner classes
    :param file_code: 生成的code
    :return: inner classes as a list of strings.
    """
    rets = []
    parser = Parser()
    parser.language = JAVA_LANGUAGE
    tmp_file_code = pickle.loads(pickle.dumps(file_code))
    if strategy == "extend":
        tmp_file_code = "public class TmpClass {\n" + file_code
    tree = parser.parse(bytes(tmp_file_code, "utf-8"))
    class_decl_query = JAVA_LANGUAGE.query(
        """
        (class_declaration) @class_decl
        """
    )
    classes = class_decl_query.captures(tree.root_node)
    if len(classes) == 1 or len(classes) == 0:
        pass
    else:
        for class_str in classes:
            modifier_nodes = [
                str(node.text, encoding="utf-8")
                for node in class_str[0].children
                if node.type == "modifiers"
            ]
            if len(modifier_nodes) != 1 and len(modifier_nodes) != 0:
                num_modifiers = len(modifier_nodes)
                raise IndexError(
                    f"number of modifiers should be 1, but was {num_modifiers}"
                )
            else:
                if len(modifier_nodes) == 1:
                    modifier_nodes = modifier_nodes[0]
                    # 去掉public的类
                    if "public" not in modifier_nodes:
                        rets.append(str(class_str[0].text, encoding="utf-8"))
                else:
                    rets.append(str(class_str[0].text, encoding="utf-8"))

    return rets


def parse_import_nodes_from_file_code(file_code: str):
    """
    从给定的代码文件内容中提取import node节点信息。为了避免噪音，需要满足两个条件：
    1. import语句必须是分号结尾
    2. import语句至多含有三个以空格区分的token

    Args:
        file_code (str): 输入的代码文件内容（最好是代码文件，其他文件中可能会被过滤掉）

    Returns:
        list: 从输入内容中提取出的import node信息，例如：
            {
                'start':import_node.start_point[0],
                'end':import_node.end_point[0],
                'text':import_stmt
            }
    """
    rets = []
    parser = Parser()
    parser.language = JAVA_LANGUAGE
    tree = parser.parse(bytes(file_code, "utf-8"))
    import_decl_query = JAVA_LANGUAGE.query(
        """
    (import_declaration) @import_decl
    """
    )
    imports = import_decl_query.captures(tree.root_node)
    for import_node, _ in imports:
        import_stmt = str(import_node.text, encoding="utf-8")
        tks = import_stmt.split()
        if import_stmt.endswith(";") and (len(tks) == 2 or len(tks) == 3):
            rets.append(
                {
                    "start": import_node.start_point[0],
                    "end": import_node.end_point[0],
                    "text": import_stmt,
                }
            )
    return rets


def parse_param_declaration_from_method_code(method_code: str):
    """
    Analyze method parameters' types and names
    :param method_code: input method, usually focal method
    :return: a dict in which the keys are parameter names, and the values are corresponding types.
    """
    params = {}
    tmp_method_code = "public class TmpClass {\n" + method_code + "}\n"
    parser = Parser()
    parser.language = JAVA_LANGUAGE
    tree = parser.parse(bytes(tmp_method_code, "utf-8"))
    method_param_query = JAVA_LANGUAGE.query(
        """
    (class_declaration 
    body: (class_body
    (method_declaration 
    parameters: (formal_parameters
    (formal_parameter 
    type: (_) @type_identifier
    name: (identifier) @param_name )
    ))))
    (class_declaration 
    body: (class_body
    (method_declaration 
    parameters: (formal_parameters
    (_
    (type_identifier) @type_identifier
    (variable_declarator name: (_) @param_name))
    ))))

    """
    )
    res = method_param_query.captures(tree.root_node)
    for type_iden, param_name in zip(res[0::2], res[1::2]):
        params[str(param_name[0].text, encoding="utf-8")] = str(
            type_iden[0].text, encoding="utf-8"
        )
    return params


def parse_method_invocation(method_code: str):
    """
    分析给定的函数中的其他函数调用情况

    Args:
        method_code (str): 给定的函数实现，通常是大模型生成的UT

    Returns:
        list<dict>: 返回一个字典的list，每个字典包含以下键值对：
            - invocation: 整体的函数调用字符串
            - invocator: 调用者的标识符，这里如果有package，也会放到一起返回
            - invoked_method_name: 被调用的方法的方法名
            - invocation_args: 被调用方法的参数列表，注意这里是带括号的实际传入参数的字符串
    """
    ret = []  # 定义一个空列表用于存储解析结果
    tmp_method_code = (
            "public class TmpClass {\n" + method_code + "}\n"
    )  # 将输入的方法代码定义到一个临时类中
    parser = Parser()  # 创建一个解析器对象
    parser.language = JAVA_LANGUAGE  # 设置解析器的语言为Java
    tree = parser.parse(bytes(tmp_method_code, "utf-8"))  # 解析临时类的方法代码，生成语法树
    # 定义一个查询语句，用于匹配方法调用
    method_invocation_query = JAVA_LANGUAGE.query(
        """
    (method_invocation 
    object: (_) @object
    name: (_) @methodNname
    arguments: (_) @args
    ) @invoke
    """
    )

    invocations = method_invocation_query.captures(tree.root_node)  # 在语法树中查找所有方法调用
    if len(invocations) % 4 != 0:  # 如果调用次数不能被4整除，则跳过此次循环
        pass
    else:
        num_iter = int(len(invocations) / 4)  # 调用次数除以4得到循环次数
        for i in range(num_iter):  # 循环处理每个方法调用
            invocation_str = str(
                invocations[i * 4][0].text, encoding="utf-8"
            )  # 获取调用的字符串形式
            invocator_obj = str(
                invocations[i * 4 + 1][0].text, encoding="utf-8"
            )  # 获取调用者对象的字符串形式
            invocated_method_name = str(
                invocations[i * 4 + 2][0].text, encoding="utf-8"
            )  # 获取被调用方法的字符串形式
            invocation_args = str(
                invocations[i * 4 + 3][0].text, encoding="utf-8"
            )  # 获取调用的参数字符串形式
            ret.append(  # 将解析结果添加到列表中
                {
                    "invocation": invocation_str,  # 调用信息
                    "invocator": invocator_obj,  # 调用者对象
                    "invoked_method_name": invocated_method_name,  # 被调用方法
                    "invocation_args": invocation_args,  # 调用参数
                }
            )
        pass
    return ret  # 返回解析结果列表


def parse_identifier_in_method_body(method_code: str):
    ret = set()
    class_code = f'public class SomeClass {{\n{method_code}\n }}'
    parser = Parser()  # 创建一个解析器对象
    parser.language = JAVA_LANGUAGE  # 设置解析器的语言为Java
    tree = parser.parse(bytes(class_code, "utf-8"))  # 解析临时类的方法代码，生成语法树

    def _parse_identifier(node):
        ret = set()
        if node.type == 'identifier':
            ret.add(str(node.text, encoding='utf-8'))
        for child in node.children:
            ret = ret.union(_parse_identifier(child))
        return ret

    def _traverse_root(root_node):
        identifiers = set()
        if root_node.type == 'method_declaration':
            for child in root_node.children:
                if child.type == 'block':
                    identifiers = identifiers.union(_parse_identifier(child))
                    return identifiers
        for child in root_node.children:
            identifiers = identifiers.union(_traverse_root(child))
        return identifiers

    identifiers = _traverse_root(tree.root_node)  # 在语法树中查找所有方法调用
    return identifiers
