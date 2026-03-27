import re
import sys
from typing import List

from utils.parsers import parse_import_stmts, _parse_class_obj

sys.path.extend([".", ".."])
import pickle
from loguru import logger
from tree_sitter import Parser
from Config import JAVA_LANGUAGE, KNOWN_ASSERTIONS
from entities.Class import Class, Interface
from entities.Method import Method, MethodInvocation, Constructor
from entities.Variable import Variable, Field, Parameter, Type


def parse_interface_declaration(interface_str: str, file: str):
    """
    This function is used to parse the interface declaration from a given interface string.
    It uses the tree-sitter query language to extract the interface and its methods.

    Args:
        interface_str (str): The interface string to parse interface declaration from.

    Returns:
        list: A list of Interface objects, each representing a method in the interface.
    """
    parser = Parser()
    parser.language = JAVA_LANGUAGE
    tree = parser.parse(bytes(interface_str, "utf-8"))
    imports = parse_import_stmts(interface_str)
    interface_declaration_nodes = [child_node for child_node in tree.root_node.children if
                                   child_node.type == 'interface_declaration']
    all_interface_objs = []
    package_declaration = [node for node in tree.root_node.children if node.type == 'package_declaration']
    if len(package_declaration) == 0:
        # logger.warning(f'Package declaration not found.')
        pkg_name = None
    else:
        # assert len(package_declaration) == 1
        pkg_name = str(package_declaration[0].text, encoding='utf-8').split()[-1]
        if not pkg_name.endswith(';'):
            logger.warning(f'Package declaration not found.')
            pkg_name = None
        else:
            pkg_name = pkg_name[:-1].strip()
    for class_declaration_node in interface_declaration_nodes:
        cls_obj = _parse_interface_obj(class_declaration_node, file)
        cls_obj._imports = pickle.loads(pickle.dumps(imports))
        cls_obj._package = pkg_name if pkg_name else ''
        cls_obj._class_signature = pkg_name + '.' + cls_obj.name if pkg_name else cls_obj.name

        # add class signature to it's methods
        for m in cls_obj._class_methods:
            m._belongs = cls_obj.signature

        all_interface_objs.append(cls_obj)

    return all_interface_objs


def _parse_interface_obj(cls_decl_node, file):
    interface_obj = Interface()
    interface_obj._file = file
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
    interface_obj._class_methods = parse_interface_methods(interface_obj._text)
    interface_obj._class_fields = parse_interface_fields(interface_obj._text)
    if 'abstract' in interface_obj.modifiers:
        interface_obj._is_abstract = True

    return interface_obj


def parse_interface_fields(class_str: str) -> List[Field]:
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
    field_decl_query = JAVA_LANGUAGE.query("""(constant_declaration) @field_decl""")
    field_attr_query = JAVA_LANGUAGE.query(
        """
        (constant_declaration
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


def parse_interface_methods(class_str: str):
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

    method_query = JAVA_LANGUAGE.query(
        """
        (method_declaration) @method_decl
        """
    )
    method_attr_query = JAVA_LANGUAGE.query(
        """
        (method_declaration
            (modifiers) @modifier
            type: (_) @ret_type
            name: (_) @name
            (formal_parameters) @params
        )
        """
    )

    methods = method_query.captures(tree.root_node).get('method_decl', [])
    for method_node in methods:
        m = Method()
        m._text = method_node.text.decode('utf-8')
        m._param_list = []
        m._local_variables = []
        m._callees = []
        m._method_body = str(method_node.text, encoding='utf-8')
        attrs = method_attr_query.captures(method_node)
        name_list = attrs.get('name', [])
        modifier_list = attrs.get('modifier', [])
        ret_type_list = attrs.get('ret_type', [])
        params_list = attrs.get('params', [])

        if len(name_list) != len(modifier_list) or len(name_list) != len(ret_type_list) or len(name_list) != len(
                params_list):
            logger.error(f"Method attribute mismatch: name {len(name_list)}, "
                         f"modifier {len(modifier_list)}, ret_type {len(ret_type_list)}, params {len(params_list)}")
            raise ValueError("Method attribute mismatch")
        attrs = zip(name_list, modifier_list, ret_type_list, params_list)

        for name, modifier, ret_type, params in attrs:
            m._method_name = str(name.text, encoding='utf-8')
            m._modifiers = str(modifier.text, encoding='utf-8').split()
            m._return_type = Type.build_type(str(ret_type.text, encoding='utf-8'))
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
                        # else:
                        #     raise Exception("Unknown node in parameter.")
                    m._param_list.append(p)

        param_strings = [str(obj) for obj in m._param_list]
        m._method_signature = str(m._return_type) + ' ' + m._method_name + '(' + ', '.join(param_strings) + ')'
        for modi in m._modifiers:
            if modi.startswith('@Test'):
                m._is_test_method = True
                break
        rets.append(pickle.loads(pickle.dumps(m)))
    return rets
