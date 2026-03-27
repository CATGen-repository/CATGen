import collections
from typing import List

from entities.Variable import Type
from utils.helper import DefaultCollection, json_serializable, is_strict_float, is_strict_integer
from utils.mappers import method_call_mapper


@json_serializable
class Class:
    _modifiers = []
    _class_name = ''
    _class_signature = ''
    _class_methods = []
    _class_fields = []
    _class_constructors = []
    _is_interface = False
    _is_abstract = False
    _is_final = False
    _is_test_class = False
    _test_class_setup = ''
    _super_classes = []
    _sub_classes = []
    _inner_classes = []
    _interfaces = []
    _project = ''
    _imports = []
    _text = []
    _declaration = ''
    _package = ''
    _file_path = ''

    def replace_import_types(self, local_classes):
        import_types = DefaultCollection()
        for im in self._imports:
            im = im.strip(';')
            symbol = im.split('.')[-1]
            if not symbol == '*':
                import_types[symbol] = {
                    'name': im.split(' ')[-1],
                    'class': None
                }
        for cls in local_classes:
            # 如果是同一个package下的类，不需要import，也加入到import_types中
            if cls.package == self.package and cls.name != self.name:
                import_types[cls.name] = {
                    'name': cls.name,
                    'class': cls
                }
            if cls.name in import_types:
                import_types[cls.name]['class'] = cls
        for filed in self._class_fields:
            filed.replace_import_types(import_types)
        for m in self._class_methods:
            m.replace_import_types(import_types)

    def method_call_mapping(self, local_classes):
        for m in self._class_methods:
            for mi in m._callees:
                if mi.object is None:
                    # 说名这是local method访问
                    param_types = []
                    for param in mi.params:
                        param_type = self.getType(m._local_variables + m.params, param)
                        param_types.append(param_type)
                    method_call_mapper(self, mi, param_types)
                else:
                    called_type = self.getType(m._local_variables + m.params, mi.object)
                    param_types = []
                    for param in mi.params:
                        param_type = self.getType(m._local_variables + m.params, param)
                        param_types.append(param_type)
                    if called_type is not None:
                        method_call_mapper(called_type.belongs_to, mi, param_types)

    def getType(self, local_vars, name, ):
        called_type = None
        if is_strict_float(name):
            called_type = Type('float', None, False)
            return called_type

        if is_strict_integer(name):
            called_type = Type('int', None, False)
            return called_type

        for var in local_vars:
            if var.name == name:
                called_type = var.type
                break

        # 有可能是参数

        # 也有可能是field的调用
        if called_type is None:
            for field in self._class_fields:
                if field.name == name:
                    called_type = field.type
                    break
        return called_type

    @property
    def fields(self):
        return self._class_fields

    @property
    def methods(self):
        return self._class_methods

    @property
    def package(self):
        return self._package

    @property
    def declaration_text(self):
        return self._declaration

    @property
    def text(self):
        return self._text

    @property
    def modifiers(self):
        return self._modifiers

    @property
    def name(self):
        return self._class_name

    @property
    def signature(self):
        return self._class_signature

    @property
    def inner_classes(self):
        return self._inner_classes

    @property
    def imports(self):
        return self._imports

    @property
    def is_abstract(self):
        return self._is_abstract


class TestClass(Class):
    _setup_methods = []


class EnumClass(Class):
    _enum_constants = []


class Interface(Class):
    _super_interfaces = []
