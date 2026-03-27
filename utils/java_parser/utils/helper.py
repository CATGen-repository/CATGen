import re
from collections import defaultdict


class DefaultCollection(defaultdict):
    def __init__(self):
        super().__init__(lambda: None)

    def __getitem__(self, key):
        if key in self:
            value = super().__getitem__(key)
            return value
        else:
            return {'name': key, 'class': None}


def json_serializable(cls):
    def convert2json(self):
        json_obj = {'NODE_TYPE': self.__class__.__name__}
        for attr in dir(self):
            attr_value = getattr(self, attr)
            if not attr.startswith("__") and not callable(attr_value) and not isinstance(
                    getattr(type(self), attr, None), property):
                value = getattr(self, attr)
                if isinstance(value, list):
                    json_obj[attr] = [item.convert2json() if hasattr(item, 'convert2json') else item for item in value]
                elif hasattr(value, 'convert2json'):
                    json_obj[attr] = value.convert2json()
                else:
                    json_obj[attr] = value
        return json_obj

    cls.convert2json = convert2json
    return cls


import os
import json


def save2file(json_obj, base_path='./data'):
    package = json_obj['_package']
    class_name = json_obj['_class_name']

    path_parts = package.split('.')
    full_path = os.path.join(base_path, *path_parts)

    os.makedirs(full_path, exist_ok=True)

    filename = f"{class_name}.json"
    full_filename = os.path.join(full_path, filename)

    with open(full_filename, 'w', encoding='utf-8') as file:
        json.dump(json_obj, file, ensure_ascii=False, indent=4)


def is_strict_float(s: str) -> bool:
    pattern = re.compile(r'^-?\d+\.\d+$')
    return bool(pattern.match(s))


def is_strict_integer(s: str) -> bool:
    pattern = re.compile(r'^-?\d+$')
    return bool(pattern.match(s))

