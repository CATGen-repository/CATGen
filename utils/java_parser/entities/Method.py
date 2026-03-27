from overrides import overrides

from entities.Variable import Type
from utils.helper import json_serializable


@json_serializable
class Method:
    _method_name = ''
    _method_body = ''
    _method_signature = ''
    _param_list = []
    _return_type = Type(name='void')
    _callees = []
    _is_test_method = False
    _local_variables = []
    _modifiers = []
    _belongs = []
    _is_constructor = False
    _text = ''

    def replace_import_types(self, import_types):
        for var in self._local_variables:
            var.replace_import_types(import_types)
        for p in self._param_list:
            p.replace_import_types(import_types)
        self._return_type.replace_import_types(import_types)

    @property
    def is_test(self):
        return self._is_test_method

    @property
    def is_constructor(self):
        return self._is_constructor

    @property
    def variables(self):
        return self._local_variables

    @property
    def belongs(self):
        return self._belongs

    @property
    def callees(self):
        return self._callees

    @property
    def name(self):
        return self._method_name

    @property
    def params(self):
        return self._param_list

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
                elif isinstance(value, str) or isinstance(value, bool):
                    json_obj[attr] = value
                else:
                    json_obj[attr] = value.convert2json()
        return json_obj


class Constructor(Method):

    def __init__(self):
        super().__init__()
        self._is_constructor = True

    @overrides
    def replace_import_types(self, import_types):
        for var in self._local_variables:
            var.replace_import_types(import_types)
        for p in self._param_list:
            p.replace_import_types(import_types)


@json_serializable
class MethodInvocation:
    _method_name = ''
    _object = None
    _param_list = []
    _belonged_type = ''
    _belongs_to = None

    @property
    def params(self):
        return self._param_list

    @property
    def object(self):
        return self._object

    @property
    def name(self):
        return self._method_name

    @property
    def belonged_type(self):
        return self._belonged_type

    @property
    def belongs_to(self):
        return self._belongs_to
