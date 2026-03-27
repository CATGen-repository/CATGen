from tree_sitter import Parser

from Config import JAVA_LANGUAGE
from utils.helper import json_serializable

parser = Parser()
parser.language = JAVA_LANGUAGE



@json_serializable
class Variable:
    _type = None
    _name = ''
    _init_value = ''

    def __str__(self):
        prefix = f'{self._type} {self._name}'
        if self._init_value != '':
            return prefix + f' = {self._init_value}'
        return prefix

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._init_value

    @property
    def type(self):
        return self._type

    def replace_import_types(self, import_types):
        self._type.replace_import_types(import_types)

    def convert2json(self):
        json_obj = {}
        for attr in dir(self):
            if not attr.startswith("__") and not callable(getattr(self, attr)):
                value = getattr(self, attr)
                if isinstance(value, list):
                    json_obj[attr] = []
                    for item in value:
                        if not isinstance(item, str):
                            json_obj[attr].append(item.convert2json())
                        else:
                            json_obj[attr].append(item)
                elif isinstance(value, str):
                    json_obj[attr] = value
                else:
                    json_obj[attr] = value.convert2json()
        return json_obj


class Field(Variable):
    _modifiers = []

    @property
    def modifiers(self):
        return self._modifiers


class Parameter(Variable):
    _modifiers = []

    def __init__(self):
        super().__init__()


@json_serializable
class Type():
    _is_generic_type = False
    _arg_list = []
    _name = []
    belongs_to = None

    def __init__(self, name='', arg_list=None, is_generic_type=False):
        if arg_list is None:
            arg_list = []
        self._is_generic_type = is_generic_type
        self._name = name
        self._arg_list = arg_list

    def __eq__(self, other):
        if not isinstance(other, Type):
            return False
        return str(self) == str(other)

    def __str__(self):
        rt = self._name
        if self._is_generic_type:
            return f"{rt}<{[','.join([str(x) for x in self._arg_list])]}>"
        else:
            return rt

    @property
    def is_generic_type(self):
        return self._is_generic_type

    @property
    def arg_list(self):
        return self._arg_list

    @staticmethod
    def build_type(type_string, method_node=None):
        type_node = parse_java_type(type_string)
        assert type_node.text.decode('utf-8') == type_string
        return build_type_helper(type_node)

    def replace_import_types(self, import_types):
        self._name, self.belongs_to = import_types[self._name]['name'], import_types[self._name]['class']
        if self._is_generic_type:
            for arg in self._arg_list:
                arg.replace_import_types(import_types)


def parse_java_type(java_type):
    java_code = f'{java_type} dummy;'
    tree = parser.parse(bytes(java_code, "utf8"))
    root_node = tree.root_node
    type_node = root_node.children[0].child_by_field_name('type')
    return type_node


# def parse_java_type(java_type):
#     java_code = f'class Dummy {{ {java_type} dummy; }}'
#     tree = parser.parse(bytes(java_code, "utf8"))
#     root_node = tree.root_node
#     type_node = root_node.descendant_for_point_range((0, 14), (0, 14 + len(java_type)))
#     return type_node


def build_type_helper(type_node):
    if type_node.type == 'generic_type':
        assert type_node.children[0].type == 'type_identifier' or type_node.children[0].type == 'scoped_type_identifier'
        assert type_node.children[1].type == 'type_arguments'
        arg_list = []
        for arg in type_node.children[1].children:
            if arg.type in ['<', '>', ',']:
                continue
            elif arg.type == 'generic_type':
                arg_list.append(build_type_helper(arg))
            else:
                arg_list.append(build_type_helper(arg))
        return Type(type_node.text.decode('utf-8'), arg_list, True)
    else:
        return Type(type_node.text.decode('utf-8'), None, False)
